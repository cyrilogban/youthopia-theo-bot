# theo/core/services/schedule_service.py

import logging
from html import escape

from telebot import TeleBot

from theo.app.container import Container
from theo.core.services.translation_service import (
    get_default_translation,
    get_translation_or_default,
)
from theo.core.services.verse_service import (
    fetch_scripture_text_by_reference,
    format_reference_message,
    get_scripture_by_category,
    get_votd_category,
)
from theo.adapters.telegram.views.keyboards import build_verse_actions_keyboard

logger = logging.getLogger(__name__)


def _render_daily_intro(chat_title: str | None, first_name: str | None, is_private: bool) -> str:
    if is_private and first_name:
        return f"Good morning, {first_name}. Here is your verse for today:"

    if not is_private and chat_title:
        return f"Good morning, {chat_title}. Here is your verse for today:"

    return "Good morning. Here is your verse for today:"


def daily_job(container: Container, bot: TeleBot) -> None:
    logger.info("Scheduler triggered daily_job()")

    repo = container.group_repo
    groups = list(repo.list_enabled_groups())
    logger.info(f"Enabled groups count: {len(groups)}")

    if not groups:
        return

    try:
        from theo.infra.supabase_verse_repo import get_votd_verse
        votd = get_votd_verse()
        if not votd:
            logger.error("Could not get VOTD verse from votd_log.")
            return

        base_translation = get_default_translation()
        base_verse = get_scripture_by_category(
            get_votd_category(),
            translation=base_translation,
        )
    except Exception:
        logger.exception("Failed to prepare the daily VOTD reference.")
        return

    reference = base_verse.reference.reference
    category = base_verse.category

    for g in groups:
        try:
            translation = get_translation_or_default(getattr(g, "translation", None))
            verse_text = (
                base_verse.text
                if translation == base_verse.translation
                else fetch_scripture_text_by_reference(reference, translation=translation)
            )

            verse_message = format_reference_message(
                reference,
                verse_text,
                translation=translation,
            )

            chat = bot.get_chat(g.chat_id)
            chat_type = getattr(chat, "type", "")
            is_private = chat_type == "private"
            chat_title = getattr(chat, "title", None)
            first_name = getattr(chat, "first_name", None)

            intro = _render_daily_intro(
                chat_title=chat_title,
                first_name=first_name,
                is_private=is_private,
            )

            bot.send_message(
                g.chat_id,
                f"{escape(intro)}\n\n{verse_message}",
                reply_markup=build_verse_actions_keyboard(
                    category,
                    reference,
                ),
                parse_mode="HTML",
            )
        except Exception:
            logger.exception(f"Failed to send daily VOTD message to {g.chat_id}")