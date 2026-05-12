# theo/app/container.py 
from __future__ import annotations

from dataclasses import dataclass

from theo.app.config import Settings
from theo.infra.db.mongo import MongoGroupRepo
from theo.infra.db.repo import GroupRepo
from theo.infra.google_calendar_client import GoogleCalendarClient
from theo.core.services.calendar_service import CalendarService


@dataclass(frozen=True)
class Container:
    settings: Settings
    group_repo: GroupRepo
    calendar_client: GoogleCalendarClient
    calendar_service: CalendarService


def build_container(settings: Settings) -> Container:
    group_repo = MongoGroupRepo(
        mongo_uri=settings.mongo_uri,
        db_name=settings.mongo_db_name,
        collection_name="groups",
    )

    calendar_client = GoogleCalendarClient(creds_path=settings.google_creds_path)
    calendar_service = CalendarService(
        client=calendar_client,
        calendar_id=settings.google_calendar_id
    )

    return Container(
        settings=settings,
        group_repo=group_repo,
        calendar_client=calendar_client,
        calendar_service=calendar_service
    )