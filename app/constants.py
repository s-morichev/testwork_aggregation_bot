import enum


class TimePeriod(enum.Enum):
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"

    @classmethod
    def values_list(cls):
        return [member.value for member in cls]


START_MESSAGE = """
Отправьте запрос в виде
{"dt_from": "2022-09-01T00:00:00",
"dt_upto": "2022-12-31T23:59:00",
"group_type": "month"}
Значение group_type может быть hour, day, month
"""

VALIDATION_ERROR_MESSAGE = """
Запрос должен быть в формате
{"dt_from": "2022-09-01T00:00:00",
"dt_upto": "2022-12-31T23:59:00",
"group_type": "month"}
Значение group_type может быть hour, day, month
"""

DATE_ORDER_ERROR_MESSAGE = """
Начальная дата должна быть меньше конечной
"""
