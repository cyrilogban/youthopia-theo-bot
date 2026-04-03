from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import random
from typing import Any
from urllib.parse import quote

import requests

from theo.core.services.translation_service import (
    get_translation_label,
    get_translation_or_default,
)


VERSE_API_URL = "https://bible-api.com/"
REQUEST_TIMEOUT_SECONDS = 15
REQUEST_RETRY_ATTEMPTS = 3
VERSE_CONFIG_PATH = Path(__file__).resolve().parents[2] / "data" / "verses.json"
EXPANDABLE_QUOTE_MIN_CHARS = 220

class VerseServiceError(RuntimeError):
    """Raised when the verse service cannot complete a request."""


class UnknownCategoryError(VerseServiceError):
    """Raised when a requested category does not exist in config."""


class VerseLookupError(VerseServiceError):
    """Raised when no verse text can be fetched for a category or reference."""


@dataclass(frozen=True)
class VerseReference:
    book: str
    chapter: int
    verse: int

    @property
    def reference(self) -> str:
        return f"{self.book} {self.chapter}:{self.verse}"


@dataclass(frozen=True)
class VerseResponse:
    category: str
    reference: VerseReference
    text: str
    translation: str



def load_verse_config() -> dict[str, Any]:
    with VERSE_CONFIG_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    categories = data.get("categories")
    if not isinstance(categories, dict) or not categories:
        raise VerseServiceError("Verse config is missing categories.")

    return data



def list_categories() -> tuple[str, ...]:
    config = load_verse_config()
    categories = tuple(config["categories"].keys())

    if any(category != category.lower() for category in categories):
        raise VerseServiceError("All category names in config must be lowercase.")

    return categories



def get_votd_category() -> str:
    config = load_verse_config()
    category = str(config.get("votd", {}).get("category", "")).strip().lower()

    if category not in config["categories"]:
        raise VerseServiceError("Configured VOTD category does not exist in categories.")

    return category



def get_scripture_by_category(
    category: str,
    exclude_reference: str | None = None,
    translation: str | None = None,
) -> VerseResponse:
    normalized_category = category.strip().lower()
    normalized_translation = get_translation_or_default(translation)
    config = load_verse_config()
    candidates = config["categories"].get(normalized_category)

    if not candidates:
        raise UnknownCategoryError(f"Unknown category: {category}")

    references = [_parse_reference(item) for item in candidates]
    if exclude_reference:
        filtered_references = [
            reference for reference in references if reference.reference != exclude_reference
        ]
        if filtered_references:
            references = filtered_references

    random.shuffle(references)

    last_error: Exception | None = None
    for reference in references:
        try:
            verse_text = _fetch_verse_text(reference, translation=normalized_translation)
            return VerseResponse(
                category=normalized_category,
                reference=reference,
                text=verse_text,
                translation=normalized_translation,
            )
        except VerseLookupError as exc:
            last_error = exc

    if last_error is not None:
        raise VerseLookupError(
            f"Could not fetch a verse for category '{normalized_category}'."
        ) from last_error

    raise VerseLookupError(f"No verse references were available for '{normalized_category}'.")



def fetch_scripture_text_by_reference(
    reference: str,
    translation: str | None = None,
) -> str:
    normalized_reference = " ".join(reference.strip().split())
    if not normalized_reference:
        raise VerseLookupError("Reference cannot be empty.")

    normalized_translation = get_translation_or_default(translation)
    encoded_reference = quote(normalized_reference, safe="")
    url = f"{VERSE_API_URL}{encoded_reference}?translation={normalized_translation}"

    last_error: Exception | None = None
    for _ in range(REQUEST_RETRY_ATTEMPTS):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            payload = response.json()

            verses = payload.get("verses")
            if isinstance(verses, list) and verses:
                return _format_api_verses(verses)

            verse_text = str(payload.get("text", "")).strip()
            if not verse_text:
                raise VerseLookupError(
                    f"Empty verse text returned for {normalized_reference}."
                )
            return " ".join(verse_text.split())
        except (requests.RequestException, ValueError, VerseLookupError) as exc:
            last_error = exc

    raise VerseLookupError(
        f"Failed to fetch verse text for {normalized_reference}."
    ) from last_error



def fetch_verse(
    category: str | None = None,
    exclude_reference: str | None = None,
    translation: str | None = None,
) -> str:
    target_category = category or get_votd_category()
    verse_response = get_scripture_by_category(
        target_category,
        exclude_reference=exclude_reference,
        translation=translation,
    )
    return format_verse_message(verse_response)



def format_reference_message(
    reference: str,
    verse_text: str,
    translation: str | None = None,
) -> str:
    normalized_translation = get_translation_or_default(translation)
    translation_label = get_translation_label(normalized_translation)
    cleaned_text = verse_text.strip()
    escaped_reference = escape(reference)
    escaped_body = escape(cleaned_text)
    quote_tag = (
        "blockquote expandable"
        if _should_use_expandable_quote(cleaned_text)
        else "blockquote"
    )
    return (
        f"\U0001F4D6 {escaped_reference} ({translation_label})\n\n"
        f"<{quote_tag}>{escaped_body}</blockquote>"
    )



def format_verse_message(verse_response: VerseResponse) -> str:
    return format_reference_message(
        verse_response.reference.reference,
        verse_response.text,
        translation=verse_response.translation,
    )



def _parse_reference(item: dict[str, Any]) -> VerseReference:
    return VerseReference(
        book=str(item["book"]).strip(),
        chapter=int(item["chapter"]),
        verse=int(item["verse"]),
    )



def _fetch_verse_text(
    reference: VerseReference,
    translation: str | None = None,
) -> str:
    return fetch_scripture_text_by_reference(reference.reference, translation=translation)



def _should_use_expandable_quote(verse_text: str) -> bool:
    return "\n" in verse_text or len(verse_text) >= EXPANDABLE_QUOTE_MIN_CHARS


def _format_api_verses(verses: list[dict[str, Any]]) -> str:
    if len(verses) == 1:
        verse_text = str(verses[0].get("text", "")).strip()
        if not verse_text:
            raise VerseLookupError("Empty verse text returned from verse payload.")
        return " ".join(verse_text.split())

    formatted_lines: list[str] = []
    for verse in verses:
        verse_number = verse.get("verse")
        verse_text = str(verse.get("text", "")).strip()
        if not verse_text or verse_number is None:
            continue

        cleaned_text = " ".join(verse_text.split())
        formatted_lines.append(f"{verse_number}. {cleaned_text}")

    if not formatted_lines:
        raise VerseLookupError("Empty multi-verse payload returned from API.")

    return "\n".join(formatted_lines)

