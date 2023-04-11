from pyrogram import Client

from app.mongo_db import MongoDatabase


class Bot(Client):
    def __init__(self, name: str, database: MongoDatabase, **kwargs):
        super().__init__(name, **kwargs)
        self.db = database
