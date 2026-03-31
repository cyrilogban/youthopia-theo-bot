from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Protocol


@dataclass(frozen=True)
class GroupRecord:
    """
    A minimal representation of a Telegram chat we store.

    Core/services should operate on clean Python objects,
    not raw MongoDB dictionaries, so the database can be swapped later.
    """
    chat_id: int
    title: Optional[str] = None
    enabled: bool = True
    translation: str = "kjv"


class GroupRepo(Protocol):
    """
    Storage contract for chats/groups.

    Any database implementation (Mongo, Postgres, mock) must provide these methods.
    """

    def upsert_group(self, record: GroupRecord) -> None:
        """Create or update a chat record."""

    def disable_group(self, chat_id: int) -> bool:
        """Disable daily broadcasts for a chat. Returns True if changed."""

    def enable_group(self, chat_id: int) -> bool:
        """Enable daily broadcasts for a chat. Returns True if changed."""

    def get_group(self, chat_id: int) -> Optional[GroupRecord]:
        """Fetch a chat by chat_id. Return None if not found."""

    def list_enabled_groups(self) -> Iterable[GroupRecord]:
        """Return all chats where enabled=True."""
