import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    mongo_uri: str
    mongo_db_name: str
    admin_ids: list[int]
    google_creds_path: str
    google_calendar_ids: list[str]


def load_settings() -> Settings:
    load_dotenv(override=True)

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    mongo_uri = os.getenv("MONGO_URI", "").strip()
    mongo_db_name = os.getenv("MONGO_DB_NAME", "theo").strip()
    google_creds_path = os.getenv("GOOGLE_CREDS_PATH", "google_credentials.json").strip()
    
    # Handle multiple calendar IDs
    google_calendar_ids_raw = os.getenv("GOOGLE_CALENDAR_ID", "").strip()
    google_calendar_ids = [
        id_.strip() 
        for id_ in google_calendar_ids_raw.split(",") 
        if id_.strip()
    ]

    admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
    admin_ids = [
        int(id_.strip())
        for id_ in admin_ids_raw.split(",")
        if id_.strip().lstrip("-").isdigit()
    ]

    if not bot_token:
        raise ValueError("BOT_TOKEN is missing. Put it in your .env file.")

    if not mongo_uri:
        raise ValueError("MONGO_URI is missing. Put it in your .env file.")

    return Settings(
        bot_token=bot_token,
        mongo_uri=mongo_uri,
        mongo_db_name=mongo_db_name,
        admin_ids=admin_ids,
        google_creds_path=google_creds_path,
        google_calendar_ids=google_calendar_ids,
    )