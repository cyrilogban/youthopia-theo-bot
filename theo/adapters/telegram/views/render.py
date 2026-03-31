from __future__ import annotations

from collections.abc import Sequence



def render_category_prompt(categories: Sequence[str]) -> str:
    return (
        "Choose a scripture category below, or use one of the Telegram menu commands.\n\n"
        f"Available categories: {', '.join(category.title() for category in categories)}"
    )



def render_unknown_category(categories: Sequence[str]) -> str:
    return (
        "I can only match these scripture categories right now.\n\n"
        f"Choose one below: {', '.join(category.title() for category in categories)}"
    )



def render_verse_lookup_error(category: str) -> str:
    return (
        f"I couldn't fetch a {category} verse right now. "
        "Please try again in a moment."
    )



def render_inline_help() -> str:
    return (
        "Use /verse to browse categories, or choose a specific menu command like "
        "/hope, /peace, or /love."
    )



def render_forward_instruction() -> str:
    return "Long-press the verse and forward it to a friend or group."
