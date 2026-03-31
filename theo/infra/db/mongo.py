from __future__ import annotations

from dataclasses import asdict
from typing import Iterable, Optional

import certifi
from pymongo import MongoClient
from pymongo.collection import Collection

from theo.infra.db.repo import GroupRecord, GroupRepo
from theo.core.services.translation_service import get_translation_or_default


class MongoGroupRepo(GroupRepo):
    """
    MongoDB implementation of GroupRepo.

    Logic:
    - Implements the contract in repo.py using Mongo.
    - Keeps Mongo details inside infra, not inside core/services.
    """

    def __init__(self, mongo_uri: str, db_name: str = "theo", collection_name: str = "groups"):
        self._client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
        self._db = self._client[db_name]
        self._col: Collection = self._db[collection_name]

        # Ensure chat_id is unique so "upsert" behaves predictably
        self._col.create_index("chat_id", unique=True)

    def upsert_group(self, record: GroupRecord) -> None:
        doc = asdict(record)
        doc["translation"] = get_translation_or_default(doc.get("translation"))
        self._col.update_one({"chat_id": record.chat_id}, {"$set": doc}, upsert=True)

    def enable_group(self, chat_id: int) -> bool:
        result = self._col.update_one({"chat_id": chat_id}, {"$set": {"enabled": True}}, upsert=True)
        return (result.modified_count > 0) or (result.upserted_id is not None)

    def disable_group(self, chat_id: int) -> bool:
        result = self._col.update_one({"chat_id": chat_id}, {"$set": {"enabled": False}})
        return result.modified_count > 0

    def get_group(self, chat_id: int) -> Optional[GroupRecord]:
        doc = self._col.find_one({"chat_id": chat_id})
        if not doc:
            return None
        return self._doc_to_record(doc)

    def list_enabled_groups(self) -> Iterable[GroupRecord]:
        cursor = self._col.find({"enabled": True})
        for doc in cursor:
            yield self._doc_to_record(doc)

    @staticmethod
    def _doc_to_record(doc: dict) -> GroupRecord:
        return GroupRecord(
            chat_id=int(doc["chat_id"]),
            title=doc.get("title"),
            enabled=bool(doc.get("enabled", True)),
            translation=get_translation_or_default(doc.get("translation")),
        )
