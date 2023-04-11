from datetime import datetime

import orjson
from pydantic import BaseModel

from app.constants import TimePeriod


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class BaseSchema(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class AggregationQuery(BaseSchema):
    dt_from: datetime
    dt_upto: datetime
    group_type: TimePeriod
