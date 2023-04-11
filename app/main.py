import asyncio

from pyrogram import idle

import app.logging_config  # noqa
from app.bot import Bot
from app.config import settings
from app.mongo_db import MongoDatabase

plugins = {"root": "plugins"}


async def main():
    with MongoDatabase(settings.mongo_uri) as database:
        bot = Bot(
            "testwork_aggregation_bot",
            database,
            api_id=settings.api_id,
            api_hash=settings.api_hash,
            bot_token=settings.bot_token,
            plugins=plugins,
        )

        await bot.start()
        await idle()


if __name__ == "__main__":
    asyncio.run(main())
