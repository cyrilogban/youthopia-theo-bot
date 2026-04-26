from telebot import TeleBot
from telebot.types import Message

from theo.app.container import Container
from theo.infra.db.repo import GroupRecord
from theo.core.policies.permissions import is_chat_admin
from theo.core.services.translation_service import (
    get_translation_label,
    get_translation_or_default,
    render_translation_options,
    validate_translation,
)


def register_groups(bot: TeleBot, container: Container) -> None:
    repo = container.group_repo

    def _is_private_chat(message: Message) -> bool:
        return getattr(message.chat, "type", "") == "private"

    def _current_translation(chat_id: int) -> str:
        record = repo.get_group(chat_id)
        if not record:
            return get_translation_or_default(None)
        return get_translation_or_default(record.translation)

    @bot.message_handler(commands=["enable_votd"])
    def enable_votd(message: Message) -> None:
        chat_id = message.chat.id
        title = getattr(message.chat, "title", None)

        if _is_private_chat(message):
            record = repo.get_group(chat_id)

            if record and record.enabled:
                bot.reply_to(message, "You are already subscribed to daily VOTD.")
                return

            translation = record.translation if record else get_translation_or_default(None)
            repo.upsert_group(
                GroupRecord(
                    chat_id=chat_id,
                    title=title,
                    enabled=True,
                    translation=translation,
                )
            )
            bot.reply_to(message, "You are now subscribed to daily VOTD.")
            return

        if not is_chat_admin(bot, message):
            bot.reply_to(
                message,
                "Only group admins can enable VOTD in groups. "
                "If you want personal daily VOTD, send /enable_votd to me in DM.",
            )
            return

        record = repo.get_group(chat_id)

        if record and record.enabled:
            bot.reply_to(message, "VOTD (Verse of the Day) is already enabled for this group.")
            return

        translation = record.translation if record else get_translation_or_default(None)
        repo.upsert_group(
            GroupRecord(
                chat_id=chat_id,
                title=title,
                enabled=True,
                translation=translation,
            )
        )
        bot.reply_to(message, "VOTD (Verse of the Day) is now enabled for this group.")

    @bot.message_handler(commands=["disable_votd"])
    def disable_votd(message: Message) -> None:
        chat_id = message.chat.id

        if _is_private_chat(message):
            record = repo.get_group(chat_id)

            if not record:
                bot.reply_to(
                    message,
                    "You are not subscribed yet. Use /enable_votd to receive daily VOTD.",
                )
                return

            if not record.enabled:
                bot.reply_to(message, "Your daily VOTD subscription is already disabled.")
                return

            changed = repo.disable_group(chat_id)

            if changed:
                bot.reply_to(message, "Your daily VOTD subscription has been disabled.")
            else:
                bot.reply_to(message, "Your daily VOTD subscription is already disabled.")
            return

        if not is_chat_admin(bot, message):
            bot.reply_to(
                message,
                "Only group admins can disable VOTD in groups. "
                "If you want to stop personal daily VOTD, send /disable_votd to me in DM.",
            )
            return

        record = repo.get_group(chat_id)

        if not record:
            bot.reply_to(message, "No subscription found for this group yet. Use /enable_votd.")
            return

        if not record.enabled:
            bot.reply_to(message, "VOTD (Verse of the Day) is already disabled for this group.")
            return

        changed = repo.disable_group(chat_id)

        if changed:
            bot.reply_to(message, "VOTD (Verse of the Day) has been disabled for this group.")
        else:
            bot.reply_to(message, "VOTD (Verse of the Day) is already disabled for this group.")

    @bot.message_handler(commands=["status"])
    def status(message: Message) -> None:
        chat_id = message.chat.id
        record = repo.get_group(chat_id)

        if _is_private_chat(message):
            if not record:
                bot.reply_to(
                    message,
                    "You are not subscribed yet. Use /enable_votd to receive daily VOTD.",
                )
                return

            if record.enabled:
                bot.reply_to(message, "You are currently subscribed to daily VOTD.")
            else:
                bot.reply_to(message, "Your daily VOTD subscription is currently disabled.")
            return

        if not record:
            bot.reply_to(message, "No subscription found for this group yet. Use /enable_votd.")
            return

        state = "enabled" if record.enabled else "disabled"
        name = record.title or "this chat"
        bot.reply_to(message, f"VOTD is currently {state} for {name}.")

    @bot.message_handler(commands=["translation"])
    def translation(message: Message) -> None:
        chat_id = message.chat.id
        title = (
            getattr(message.chat, "title", None)
            or getattr(message.chat, "first_name", None)
        )
        record = repo.get_group(chat_id)
        is_private = _is_private_chat(message)

        command_text = (message.text or "").strip()
        parts = command_text.split(maxsplit=1)

        if len(parts) == 1:
            current_translation = _current_translation(chat_id)
            subject = "Your" if is_private else "This chat's"
            bot.reply_to(
                message,
                f"{subject} current translation is {get_translation_label(current_translation)}.\n\n"
                f"Available translations: {render_translation_options()}\n\n"
                "Use:\n"
                "/translation kjv\n"
                "/translation web\n"
                "/translation bbe\n"
                "/translation asv",
            )
            return

        try:
            translation_code = validate_translation(parts[1])
        except ValueError:
            bot.reply_to(
                message,
                "Unsupported translation.\n\n"
                f"Available translations: {render_translation_options()}\n\n"
                "Use one of:\n"
                "/translation kjv\n"
                "/translation web\n"
                "/translation bbe\n"
                "/translation asv",
            )
            return

        if not is_private and not is_chat_admin(bot, message):
            bot.reply_to(
                message,
                "Only group admins can change translation in groups. "
                "If you want a personal translation, send /translation to me in DM.",
            )
            return

        enabled = record.enabled if record else False
        saved_title = record.title if record and record.title else title

        repo.upsert_group(
            GroupRecord(
                chat_id=chat_id,
                title=saved_title,
                enabled=enabled,
                translation=translation_code,
            )
        )

        if is_private and message.from_user:
            from theo.infra.supabase_user_repo import update_user_translation
            update_user_translation(message.from_user.id, translation_code)

        if is_private:
            bot.reply_to(
                message,
                f"Your translation has been set to {get_translation_label(translation_code)}."
            )
            return

        bot.reply_to(
            message,
            f"This chat translation has been set to {get_translation_label(translation_code)}."
        )