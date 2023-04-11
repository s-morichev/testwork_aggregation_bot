import logging

import orjson
from pydantic import ValidationError
from pyrogram import Client, filters
from pyrogram.types import Message

from app.bot import Bot
from app.constants import (
    DATE_ORDER_ERROR_MESSAGE,
    START_MESSAGE,
    VALIDATION_ERROR_MESSAGE,
)
from app.schemas import AggregationQuery

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("start"))
async def start_handler(bot, msg):
    await msg.reply(text=START_MESSAGE)


@Client.on_message(filters.text & filters.private)
async def aggregate(bot: Bot, msg: Message):
    logger.info("Receive query %s from chat id %s", msg.text, msg.chat.id)
    try:
        query = AggregationQuery.parse_raw(str(msg.text))
    except ValidationError:
        await msg.reply(VALIDATION_ERROR_MESSAGE)
        return
    if query.dt_from >= query.dt_upto:
        await msg.reply(DATE_ORDER_ERROR_MESSAGE)
        return

    result = await bot.db.aggregate_salary(
        query.dt_from, query.dt_upto, query.group_type
    )
    result = orjson.dumps(result, option=orjson.OPT_OMIT_MICROSECONDS).decode()
    await msg.reply(result)
    logger.info("Sent result %s to chat id %s", result, msg.chat.id)
