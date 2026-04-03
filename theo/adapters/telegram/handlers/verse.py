from __future__ import annotations

import logging

import telebot
from telebot.types import CallbackQuery

from theo.adapters.telegram.views.keyboards import (
    build_category_picker_compact,
    build_verse_actions_keyboard,
    build_dm_help_buttons,
    build_group_help_buttons,
)
from theo.adapters.telegram.views.render import (
    render_category_prompt,
    render_forward_instruction,
    render_inline_help,
    render_unknown_category,
    render_verse_lookup_error,
)
from theo.app.container import Container
from theo.core.services.category_detection_service import (
    detect_category,
    should_handle_category_request,
)
from theo.core.services.translation_service import get_translation_or_default
from theo.core.services.verse_service import (
    UnknownCategoryError,
    VerseLookupError,
    format_verse_message,
    get_scripture_by_category,
    list_categories,
)


logger = logging.getLogger(__name__)
CALLBACK_PREFIX = "verse|"



def register_verse(bot: telebot.TeleBot, container: Container) -> None:
    repo = container.group_repo

    def _available_categories() -> tuple[str, ...]:
        return list_categories()

    def _category_picker():
        return build_category_picker_compact(_available_categories())

    def _translation_for_chat(chat_id: int) -> str:
        record = repo.get_group(chat_id)
        if not record:
            return get_translation_or_default(None)
        return get_translation_or_default(record.translation)

    def _reply_with_category_verse(
        message: telebot.types.Message,
        category: str,
        exclude_reference: str | None = None,
    ) -> None:
        try:
            translation = _translation_for_chat(message.chat.id)
            verse_response = get_scripture_by_category(
                category,
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
        except UnknownCategoryError:
            bot.reply_to(
                message,
                render_unknown_category(_available_categories()),
                reply_markup=_category_picker(),
            )
        except VerseLookupError:
            logger.exception("Failed to fetch scripture for category '%s'.", category)
            bot.reply_to(
                message,
                render_verse_lookup_error(category),
                reply_markup=_category_picker(),
            )

    def _edit_with_category_verse(
        call: CallbackQuery,
        category: str,
        exclude_reference: str | None = None,
    ) -> None:
        try:
            translation = _translation_for_chat(call.message.chat.id)
            verse_response = get_scripture_by_category(
                category,
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
        except UnknownCategoryError:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=render_unknown_category(_available_categories()),
                reply_markup=_category_picker(),
            )
            bot.answer_callback_query(call.id)
        except VerseLookupError:
            logger.exception("Failed to fetch scripture for category '%s'.", category)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=render_verse_lookup_error(category),
                reply_markup=_category_picker(),
            )
            bot.answer_callback_query(call.id)

    def _parse_callback_data(data: str) -> tuple[str, list[str]]:
        parts = data.split("|", 3)
        if len(parts) < 2 or parts[0] != "verse":
            raise ValueError("Unsupported callback data.")
        return parts[1], parts[2:]

    @bot.message_handler(commands=["faith"])
    def _faith_command(message: telebot.types.Message) -> None:
        _reply_with_category_verse(message, "faith")

    @bot.message_handler(commands=["love"])
    def _love_command(message: telebot.types.Message) -> None:
        _reply_with_category_verse(message, "love")

    @bot.message_handler(commands=["peace"])
    def _peace_command(message: telebot.types.Message) -> None:
        _reply_with_category_verse(message, "peace")

    @bot.message_handler(commands=["joy"])
    def _joy_command(message: telebot.types.Message) -> None:
        _reply_with_category_verse(message, "joy")

    @bot.message_handler(commands=["hope"])
    def _hope_command(message: telebot.types.Message) -> None:
        _reply_with_category_verse(message, "hope")

    @bot.message_handler(commands=["patience"])
    def _patience_command(message: telebot.types.Message) -> None:
        _reply_with_category_verse(message, "patience")

    @bot.message_handler(commands=["forgiveness"])
    def _forgiveness_command(message: telebot.types.Message) -> None:
        _reply_with_category_verse(message, "forgiveness")

    @bot.message_handler(commands=["verse"])
    def _verse_command(message: telebot.types.Message) -> None:
        command_text = (message.text or "").strip()
        parts = command_text.split(maxsplit=1)

        if len(parts) == 2:
            category = detect_category(parts[1], _available_categories())
            if category is None:
                bot.reply_to(
                    message,
                    render_unknown_category(_available_categories()),
                    reply_markup=_category_picker(),
                )
                return

            _reply_with_category_verse(message, category)
            return

        bot.reply_to(
            message,
            render_category_prompt(_available_categories()),
            reply_markup=_category_picker(),
        )

    @bot.message_handler(
        func=lambda message: should_handle_category_request(
            getattr(message, "text", ""),
            list_categories(),
        )
    )
    def _category_request(message: telebot.types.Message) -> None:
        category = detect_category(message.text or "", _available_categories())
        if category is None:
            return
        _reply_with_category_verse(message, category)

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

        if action == "category" and payload:
            _edit_with_category_verse(call, payload[0])
            return

        if action == "help":
            # Show category buttons for help in both DMs and groups
            help_text = (
                "📖 *What would you like to explore today?*\n\n"
                "Pick a theme below to see related scripture. You can also use commands like `/enable_votd`, `/disable_votd`, or `/translation`."
            )
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=help_text,
                reply_markup=build_category_picker_compact(_available_categories()),
                parse_mode="Markdown"
            )
            bot.answer_callback_query(call.id)
            return

        if action == "votd_enable":
            bot.answer_callback_query(
                call.id,
                "Use /enable_votd command to subscribe to daily verses",
                show_alert=True
            )
            return

        if action == "votd_disable":
            bot.answer_callback_query(
                call.id,
                "Use /disable_votd command to unsubscribe from daily verses",
                show_alert=True
            )
            return

        if action == "translation":
            bot.answer_callback_query(
                call.id,
                "Use /translation to view or change your Bible translation (kjv, web, bbe, asv)",
                show_alert=True
            )
            return

        bot.answer_callback_query(call.id)

  

