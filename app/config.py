from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_db_name: str
    mongo_uri: str
    api_id: str
    api_hash: str
    bot_token: str


env_local = Path(__file__).parent.parent / ".env.local"
settings = Settings(_env_file=env_local)
