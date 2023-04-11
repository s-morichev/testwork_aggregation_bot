from datetime import datetime, timedelta
from pathlib import Path

import bson
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from app.config import settings
from app.constants import TimePeriod


async def _load_bson_data(collection: AsyncIOMotorCollection, bson_path: Path):
    content = bson.decode_all(bson_path.read_bytes())
    await collection.insert_many(content)


async def _load_init_data(db: AsyncIOMotorDatabase):
    count = await db.sample_collection.count_documents({})
    if count == 0:
        filepath = Path(__file__).parent / "sampleDB" / "sample_collection.bson"
        await _load_bson_data(db.sample_collection, filepath)


_aggregate_salary_parameters = {
    TimePeriod.MONTH: ({"year": {"$year": "$dt"}, "month": {"$month": "$dt"}}, "month"),
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
        self._client = AsyncIOMotorClient(
            settings.mongo_uri, serverSelectionTimeoutMS=5000
        )
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
