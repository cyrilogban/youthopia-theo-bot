from __future__ import annotations

from collections.abc import Sequence

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


INLINE_ACTION_PREFIX = "verse"


def build_verse_actions_keyboard(
    category: str,
    reference: str,
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            "Another Verse",
            callback_data=f"{INLINE_ACTION_PREFIX}|another|{category}|{reference}",
        ),
        InlineKeyboardButton(
            "Forward Verse",
            callback_data=f"{INLINE_ACTION_PREFIX}|forward",
        ),
    )
    keyboard.row(
        InlineKeyboardButton(
            "Help",
            callback_data=f"{INLINE_ACTION_PREFIX}|help",
        ),
    )
    return keyboard


def build_category_picker(categories: Sequence[str]) -> InlineKeyboardMarkup:
    """Build inline keyboard with category buttons (2 per row)."""
    keyboard = InlineKeyboardMarkup()

    row: list[InlineKeyboardButton] = []
    for category in categories:
        row.append(
            InlineKeyboardButton(
                category.title(),
                callback_data=f"{INLINE_ACTION_PREFIX}|category|{category}",
            )
        )
        if len(row) == 2:
            keyboard.row(*row)
            row = []

    if row:
        keyboard.row(*row)

    keyboard.row(
        InlineKeyboardButton(
            "Help",
            callback_data=f"{INLINE_ACTION_PREFIX}|help",
        ),
    )
    return keyboard


def build_category_picker_compact(categories: Sequence[str]) -> InlineKeyboardMarkup:
    """Build compact inline keyboard with emoji category buttons (3 per row, excludes forgiveness)."""
    
    # Emoji mapping for each category
    emoji_map = {
        "faith": "🙏",
        "love": "❤️",
        "peace": "☮️",
        "joy": "😊",
        "hope": "✨",
        "patience": "⏳",
        "forgiveness": "🕊️",
    }
    
    # Exclude forgiveness
    excluded = {"forgiveness"}
    filtered_categories = [cat for cat in categories if cat not in excluded]
    
    keyboard = InlineKeyboardMarkup()
    
    row: list[InlineKeyboardButton] = []
    for category in filtered_categories:
        emoji = emoji_map.get(category, "📖")
        label = f"{emoji} {category.title()}"
        
        row.append(
            InlineKeyboardButton(
                label,
                callback_data=f"{INLINE_ACTION_PREFIX}|category|{category}",
            )
        )
        if len(row) == 3:  # 3 per row
            keyboard.row(*row)
            row = []
    
    if row:
        keyboard.row(*row)
    
    return keyboard


def build_help_button_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard with a single /help button."""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            "📖 /help",
            callback_data=f"{INLINE_ACTION_PREFIX}|help",
        )
    )
    return keyboard


def build_category_picker_single_row(categories: Sequence[str]) -> InlineKeyboardMarkup:
    """Build category buttons all in ONE row (for group mention responses)."""
    
    # Emoji mapping for each category
    emoji_map = {
        "faith": "🙏",
        "love": "❤️",
        "peace": "☮️",
        "joy": "😊",
        "hope": "✨",
        "patience": "⏳",
        "forgiveness": "🕊️",
    }
    
    # Exclude forgiveness
    excluded = {"forgiveness"}
    filtered_categories = [cat for cat in categories if cat not in excluded]
    
    keyboard = InlineKeyboardMarkup()
    row: list[InlineKeyboardButton] = []
    
    for category in filtered_categories:
        emoji = emoji_map.get(category, "📖")
        
        row.append(
            InlineKeyboardButton(
                emoji,
                callback_data=f"{INLINE_ACTION_PREFIX}|category|{category}",
            )
        )
    
    if row:
        keyboard.row(*row)
    
    return keyboard


def build_dm_help_buttons() -> InlineKeyboardMarkup:
    """Build keyboard with DM help buttons (Enable VOTD, Disable VOTD, Translation)."""
    keyboard = InlineKeyboardMarkup()
    
    keyboard.row(
        InlineKeyboardButton(
            "📖 Enable VOTD",
            callback_data=f"{INLINE_ACTION_PREFIX}|votd_enable",
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            "🚫 Disable VOTD",
            callback_data=f"{INLINE_ACTION_PREFIX}|votd_disable",
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            "🔤 Change Translation",
            callback_data=f"{INLINE_ACTION_PREFIX}|translation",
        )
    )
    
    return keyboard


def build_group_help_buttons(categories: Sequence[str]) -> InlineKeyboardMarkup:
    """Build inline keyboard with category buttons for group help (2 per row)."""
    
    # Emoji mapping for each category
    emoji_map = {
        "faith": "🙏",
        "love": "❤️",
        "peace": "☮️",
        "joy": "😊",
        "hope": "✨",
        "patience": "⏳",
        "forgiveness": "🕊️",
    }
    
    # Exclude forgiveness
    excluded = {"forgiveness"}
    filtered_categories = [cat for cat in categories if cat not in excluded]
    
    keyboard = InlineKeyboardMarkup()
    
    row: list[InlineKeyboardButton] = []
    for category in filtered_categories:
        emoji = emoji_map.get(category, "📖")
        label = f"{emoji} {category.title()}"
        
        row.append(
            InlineKeyboardButton(
                label,
                callback_data=f"{INLINE_ACTION_PREFIX}|category|{category}",
            )
        )
        if len(row) == 2:  # 2 per row
            keyboard.row(*row)
            row = []
    
    if row:
        keyboard.row(*row)
    
    return keyboard
 