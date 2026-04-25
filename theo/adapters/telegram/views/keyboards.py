from __future__ import annotations

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

INLINE_ACTION_PREFIX = "verse"


def build_verse_actions_keyboard(
    category: str,
    reference: str,
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            "Save",
            callback_data=f"{INLINE_ACTION_PREFIX}|save|{category}|{reference}",
        ),
        InlineKeyboardButton(
            "Next",
            callback_data=f"{INLINE_ACTION_PREFIX}|another|{category}|{reference}",
        ),
        InlineKeyboardButton(
            "Share",
            callback_data=f"{INLINE_ACTION_PREFIX}|forward",
        ),
    )
    return keyboard


def build_help_button_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            "/help",
            callback_data=f"{INLINE_ACTION_PREFIX}|help",
        )
    )
    return keyboard


def build_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build the persistent reply keyboard that sits in the grid menu."""
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        is_persistent=True,
    )
    keyboard.row(KeyboardButton("My Profile"))
    keyboard.row(
        KeyboardButton("Saved Verses"),
        KeyboardButton("Verse History"),
    )
    keyboard.row(
        KeyboardButton("Translation"),
        KeyboardButton("Tone"),
    )
    return keyboard