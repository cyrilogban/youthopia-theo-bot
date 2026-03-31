from __future__ import annotations

import re
from typing import Iterable


REQUEST_HINTS = ("scripture", "verse", "bible", "word")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def detect_category(text: str, categories: Iterable[str]) -> str | None:
    normalized_text = normalize_text(text)
    if not normalized_text:
        return None

    for category in categories:
        if re.search(rf"\b{re.escape(category)}\b", normalized_text):
            return category

    return None


def should_handle_category_request(text: str, categories: Iterable[str]) -> bool:
    normalized_text = normalize_text(text)
    if not normalized_text or normalized_text.startswith("/"):
        return False

    category = detect_category(normalized_text, categories)
    if category is None:
        return False

    return normalized_text == category or any(hint in normalized_text for hint in REQUEST_HINTS)
