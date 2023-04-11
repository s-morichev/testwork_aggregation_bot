"""Вспомогательный скрипт для загрузки тестовых данных."""
import asyncio
import sys
from pathlib import Path

import bson
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from app.config import settings


async def load_bson_data(collection: AsyncIOMotorCollection, bson_path: Path):
    content = bson.decode_all(bson_path.read_bytes())
    await collection.insert_many(content)


async def load_init_data(dir_path: str):
    client = AsyncIOMotorClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
    collection = client[settings.mongo_db_name].sample_collection
    count = await collection.count_documents({})
    if count > 0:
        print(f"There is already documents in collection {collection.name}")
    else:
        filepath = Path(dir_path).resolve() / "sample_collection.bson"
        try:
            await load_bson_data(collection, filepath)
            count = await collection.count_documents({})
        except Exception as err:
            print(f"Error while loading: {err}")
            sys.exit(1)
        finally:
            client.close()

        print(f"Loaded {count} documents into collection {collection.name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 load_test_data.py /path/to/folder_with_bson/")
        sys.exit(2)
    asyncio.run(load_init_data(sys.argv[1]))
