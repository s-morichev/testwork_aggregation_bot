from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.constants import TimePeriod

# словарь кортежей из двух элемнтов
# 1 элемент - dateParts для получения даты начала периода времени
# 2 элемент - название time unit для $densify range unit
_aggregate_salary_parameters = {
    TimePeriod.MONTH: ({"year": {"$year": "$dt"}, "month": {"$month": "$dt"}}, "month"),
    TimePeriod.WEEK: (
        {"isoWeekYear": {"$year": "$dt"}, "isoWeek": {"$week": "$dt"}},
        "week",
    ),
    TimePeriod.DAY: (
        {
            "year": {"$year": "$dt"},
            "month": {"$month": "$dt"},
            "day": {"$dayOfMonth": "$dt"},
        },
        "day",
    ),
    TimePeriod.HOUR: (
        {
            "year": {"$year": "$dt"},
            "month": {"$month": "$dt"},
            "day": {"$dayOfMonth": "$dt"},
            "hour": {"$hour": "$dt"},
        },
        "hour",
    ),
}


class MongoDatabase:
    def __init__(self, mongo_uri):
        self._client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
        self._db = self._client[settings.mongo_db_name]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

    async def aggregate_salary(
        self, start_datetime: datetime, end_datetime: datetime, group_type: TimePeriod
    ):
        parameters = _aggregate_salary_parameters.get(group_type)
        if parameters is None:
            raise ValueError(f"Group_type must be one of {TimePeriod.values_list()}")
        date_parts, mongo_time_unit = parameters

        pipeline = [
            # фильтруем документы в заданном диапазоне
            {"$match": {"dt": {"$gte": start_datetime, "$lte": end_datetime}}},
            # добавляем дату начала диапазона к каждому документу
            {"$set": {"period_start": {"$dateFromParts": date_parts}}},
            # добавляем документы с пропущенной датой
            {
                "$densify": {
                    "field": "period_start",
                    "range": {
                        "step": 1,
                        "unit": mongo_time_unit,
                        "bounds": [
                            start_datetime,
                            end_datetime + timedelta(milliseconds=1),
                        ],
                    },
                }
            },
            # группируем документы по дате начала диапазона и суммируем выплаты
            {
                "$group": {
                    "_id": "$period_start",
                    "salary_in_period": {"$sum": "$value"},
                }
            },
            # сортируем по дате
            {"$sort": {"_id": 1}},
            # собираем выплаты и даты в массивы
            {
                "$group": {
                    "_id": "null",
                    "dataset": {"$push": "$salary_in_period"},
                    "labels": {"$push": "$_id"},
                }
            },
        ]

        cursor = self._db.sample_collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        result = result[0]
        del result["_id"]
        return result
