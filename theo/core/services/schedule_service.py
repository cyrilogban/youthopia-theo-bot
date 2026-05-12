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
from theo.core.services.tone_service import get_tone_intro

logger = logging.getLogger(__name__)


def daily_job(container: Container, bot: TeleBot) -> None:
    logger.info("Scheduler triggered daily_job()")

    # 1. Daily Calendar Reminders for Admin
    if container.settings.admin_ids:
        try:
            summary = container.calendar_service.generate_daily_summary()
            # Send to the primary admin (first in list)
            admin_id = container.settings.admin_ids[0]
            bot.send_message(admin_id, summary, parse_mode="Markdown")
            logger.info(f"Daily calendar summary sent to admin {admin_id}")
        except Exception:
            logger.exception("Failed to send daily calendar summary to admin.")

    # 2. Daily VOTD for Groups
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

            # Get tone-based intro
            if is_private:
                # For DMs get the user's tone preference
                from theo.infra.supabase_user_repo import get_user
                from theo.infra.db.repo import GroupRecord
                user = None
                try:
                    # Find user by chat_id since chat_id == telegram_id in DMs
                    user = get_user(g.chat_id)
                except Exception:
                    pass

                name = first_name or "Friend"
                telegram_id = g.chat_id if is_private else None
                intro = get_tone_intro(telegram_id, name)
            else:
                name = chat_title or "YouThopia family"
                intro = f"Good morning, {name}. Here is your verse for today."

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