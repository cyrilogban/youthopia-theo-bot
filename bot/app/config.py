import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    mongo_uri: str
    mongo_db_name: str


def load_settings() -> Settings:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    mongo_uri = os.getenv("MONGO_URI", "").strip()
    mongo_db_name = os.getenv("MONGO_DB_NAME", "theo").strip()

    if not bot_token:
        raise ValueError("BOT_TOKEN is missing. Put it in your .env file.")

    if not mongo_uri:
        raise ValueError("MONGO_URI is missing. Put it in your .env file.")

    return Settings(
        bot_token=bot_token,
        mongo_uri=mongo_uri,
        mongo_db_name=mongo_db_name,
    )