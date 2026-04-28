from __future__ import annotations

import logging

import telebot
from telebot.types import CallbackQuery

from theo.adapters.telegram.views.keyboards import (
    build_verse_actions_keyboard,
)
from theo.adapters.telegram.views.render import (
    render_forward_instruction,
    render_verse_lookup_error,
)
from theo.app.container import Container
from theo.core.services.translation_service import get_translation_or_default
from theo.core.services.verse_service import (
    UnknownCategoryError,
    VerseLookupError,
    format_verse_message,
    get_scripture_by_category,
    list_categories,
)
from theo.infra.supabase_user_repo import log_verse_to_history


logger = logging.getLogger(__name__)
CALLBACK_PREFIX = "verse|"


def register_verse(bot: telebot.TeleBot, container: Container) -> None:
    repo = container.group_repo

    def _translation_for_chat(chat_id: int) -> str:
        record = repo.get_group(chat_id)
        if not record:
            return get_translation_or_default(None)
        return get_translation_or_default(record.translation)

    def _resolve_category(category: str) -> str:
        if category == "general":
            from theo.infra.supabase_verse_repo import get_votd_category as get_day_category
            return get_day_category()
        return category

    def _reply_with_category_verse(
        message: telebot.types.Message,
        category: str,
        exclude_reference: str | None = None,
    ) -> None:
        try:
            resolved_category = _resolve_category(category)
            translation = _translation_for_chat(message.chat.id)
            verse_response = get_scripture_by_category(
                resolved_category,
                exclude_reference=exclude_reference,
                translation=translation,
            )
            bot.reply_to(
                message,
                format_verse_message(verse_response),
                reply_markup=build_verse_actions_keyboard(
                    verse_response.category,
                    verse_response.reference.reference,
                ),
                parse_mode="HTML",
            )
            
            # Log to verse history for private chats only
            if message.chat.type == "private":
                log_verse_to_history(
                    telegram_id=message.from_user.id,
                    book=verse_response.reference.book,
                    chapter=verse_response.reference.chapter,
                    verse=verse_response.reference.verse,
                    category=verse_response.category,
                    delivery_path="category_command",
                    translation=translation,
                )
        except (UnknownCategoryError, VerseLookupError):
            logger.exception("Failed to fetch scripture for category '%s'.", category)
            bot.reply_to(message, "Could not fetch a verse right now. Please try again.")

    def _edit_with_category_verse(
        call: CallbackQuery,
        category: str,
        exclude_reference: str | None = None,
    ) -> None:
        try:
            resolved_category = _resolve_category(category)
            translation = _translation_for_chat(call.message.chat.id)
            verse_response = get_scripture_by_category(
                resolved_category,
                exclude_reference=exclude_reference,
                translation=translation,
            )
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=format_verse_message(verse_response),
                reply_markup=build_verse_actions_keyboard(
                    verse_response.category,
                    verse_response.reference.reference,
                ),
                parse_mode="HTML",
            )
            bot.answer_callback_query(call.id)
            
            # Log to verse history for private chats only
            if call.message.chat.type == "private":
                log_verse_to_history(
                    telegram_id=call.from_user.id,
                    book=verse_response.reference.book,
                    chapter=verse_response.reference.chapter,
                    verse=verse_response.reference.verse,
                    category=verse_response.category,
                    delivery_path="next_button",
                    translation=translation,
                )
        except (UnknownCategoryError, VerseLookupError):
            logger.exception("Failed to fetch scripture for category '%s'.", category)
            bot.answer_callback_query(call.id, "Could not fetch a verse. Try again.")

    def _parse_callback_data(data: str) -> tuple[str, list[str]]:
        parts = data.split("|", 3)
        if len(parts) < 2 or parts[0] != "verse":
            raise ValueError("Unsupported callback data.")
        return parts[1], parts[2:]

    @bot.callback_query_handler(
        func=lambda call: str(getattr(call, "data", "")).startswith(CALLBACK_PREFIX)
    )
    def _verse_callbacks(call: CallbackQuery) -> None:
        try:
            action, payload = _parse_callback_data(call.data)
        except ValueError:
            bot.answer_callback_query(call.id)
            return

        if action == "another" and len(payload) == 2:
            _edit_with_category_verse(
                call,
                payload[0],
                exclude_reference=payload[1],
            )
            return

        if action == "forward":
            bot.answer_callback_query(
                call.id,
                render_forward_instruction(),
                show_alert=True,
            )
            return

        if action == "save" and len(payload) == 2:
            category = payload[0]
            reference = payload[1]

            try:
                parts = reference.split(" ")
                book = " ".join(parts[:-1])
                chapter_verse = parts[-1].split(":")
                chapter = int(chapter_verse[0])
                verse = int(chapter_verse[1])

                from theo.infra.supabase_user_repo import save_verse
                telegram_id = call.from_user.id

                saved = save_verse(
                    telegram_id=telegram_id,
                    book=book,
                    chapter=chapter,
                    verse=verse,
                    category=category,
                )

                if saved:
                    bot.answer_callback_query(
                        call.id,
                        "Verse saved successfully.",
                        show_alert=True,
                    )
                else:
                    bot.answer_callback_query(
                        call.id,
                        "This verse is already in your saved verses.",
                        show_alert=True,
                    )

            except Exception:
                logger.exception("Failed to save verse.")
                bot.answer_callback_query(
                    call.id,
                    "Could not save verse right now. Please try again.",
                    show_alert=True,
                )
            return

        bot.answer_callback_query(call.id)