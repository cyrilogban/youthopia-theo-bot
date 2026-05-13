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
            switch_inline_query=reference,
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


def build_user_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build the persistent reply keyboard for regular users."""
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        is_persistent=True,
    )
    keyboard.row(KeyboardButton("My Profile"))
    keyboard.row(
        KeyboardButton("Saved Verses"),
        KeyboardButton("Verse History"),
        KeyboardButton("Subscription"),
    )
    keyboard.row(
        KeyboardButton("Translation"),
        KeyboardButton("Tone"),
        KeyboardButton("Ask Anonymously"),
    )
    return keyboard


def build_admin_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build the persistent reply keyboard for admins."""
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        is_persistent=True,
    )
    keyboard.row(KeyboardButton("My Profile"))
    keyboard.row(
        KeyboardButton("Saved Verses"),
        KeyboardButton("Verse History"),
        KeyboardButton("Subscription"),
    )
    keyboard.row(
        KeyboardButton("Translation"),
        KeyboardButton("Tone"),
        KeyboardButton("Ask Anonymously"),
    )
    keyboard.row(
        KeyboardButton("My Schedule"),
        KeyboardButton("Mass Broadcast"),
    )
    return keyboard