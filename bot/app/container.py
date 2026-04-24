# theo/app/container.py 
from __future__ import annotations

from dataclasses import dataclass

from theo.app.config import Settings
from theo.infra.db.mongo import MongoGroupRepo
from theo.infra.db.repo import GroupRepo


@dataclass(frozen=True)
class Container:
    settings: Settings
    group_repo: GroupRepo


def build_container(settings: Settings) -> Container:
    group_repo = MongoGroupRepo(
        mongo_uri=settings.mongo_uri,
        db_name=settings.mongo_db_name,
        collection_name="groups",
    )
    return Container(settings=settings, group_repo=group_repo)