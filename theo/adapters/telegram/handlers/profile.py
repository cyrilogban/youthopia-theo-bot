import logging
import telebot

from theo.app.container import Container
from theo.infra.supabase_user_repo import get_user
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)


def build_profile_inline_buttons() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Change Translation", callback_data="profile|translation"),
        InlineKeyboardButton("Change Tone", callback_data="profile|tone"),
    )
    keyboard.row(
        InlineKeyboardButton("Saved Verses", callback_data="profile|saved_verses"),
        InlineKeyboardButton("Verse History", callback_data="profile|verse_history"),
    )
    return keyboard


def register_profile(bot: telebot.TeleBot, container: Container) -> None:

    @bot.message_handler(commands=["profile"])
    def _profile(message: telebot.types.Message) -> None:
        _send_profile(bot, message)

    @bot.message_handler(
        func=lambda message: message.text == "My Profile",
        content_types=["text"]
    )
    def _profile_button(message: telebot.types.Message) -> None:
        _send_profile(bot, message)

    @bot.message_handler(
        func=lambda message: message.text == "Saved Verses",
        content_types=["text"]
    )
    def _saved_verses_button(message: telebot.types.Message) -> None:
        from theo.infra.supabase_user_repo import get_saved_verses
        from theo.core.services.verse_service import fetch_scripture_text_by_reference
        from theo.core.services.translation_service import get_translation_or_default

        telegram_id = message.from_user.id
        verses = get_saved_verses(telegram_id)

        if not verses:
            bot.send_message(
                message.chat.id,
                "You have no saved verses yet.\n\nTap Save on any verse to save it here."
            )
            return

        record = container.group_repo.get_group(message.chat.id)
        translation = get_translation_or_default(
            record.translation if record else None
        )

        sections = []
        for i, v in enumerate(verses, start=1):
            book = v.get("book", "")
            chapter = v.get("chapter", "")
            verse = v.get("verse", "")
            reference = f"{book} {chapter}:{verse}"

            try:
                verse_text = fetch_scripture_text_by_reference(
                    reference,
                    translation=translation,
                )
            except Exception:
                verse_text = "Could not fetch verse text."

            sections.append(
                f"{i}. {reference} ({translation.upper()})\n{verse_text}"
            )

        saved_text = "Your Saved Verses:\n\n" + "\n\n".join(sections)

        bot.send_message(
            message.chat.id,
            saved_text,
        )

    @bot.message_handler(
        func=lambda message: message.text == "Verse History",
        content_types=["text"]
    )
    def _verse_history_button(message: telebot.types.Message) -> None:
        bot.send_message(
            message.chat.id,
            "*Verse History*\n\nThis feature is coming soon!",
            parse_mode="Markdown"
        )

    @bot.message_handler(
        func=lambda message: message.text == "Translation",
        content_types=["text"]
    )
    def _change_translation_button(message: telebot.types.Message) -> None:
        bot.send_message(
            message.chat.id,
            "Use /translation to view or change your Bible translation.\n\nAvailable: KJV, WEB, BBE, ASV"
        )

    @bot.message_handler(
        func=lambda message: message.text == "Tone",
        content_types=["text"]
    )
    def _change_tone_button(message: telebot.types.Message) -> None:
        bot.send_message(
            message.chat.id,
            "*Change Tone*\n\nThis feature is coming soon!",
            parse_mode="Markdown"
        )

    @bot.callback_query_handler(
        func=lambda call: str(getattr(call, "data", "")).startswith("profile|")
    )
    def _profile_callbacks(call: telebot.types.CallbackQuery) -> None:
        action = call.data.split("|")[1]

        if action == "translation":
            bot.answer_callback_query(
                call.id,
                "Use /translation to change your Bible translation",
                show_alert=True
            )

        elif action == "tone":
            bot.answer_callback_query(
                call.id,
                "Change Tone feature coming soon!",
                show_alert=True
            )

        elif action == "saved_verses":
            from theo.infra.supabase_user_repo import get_saved_verses
            from theo.core.services.verse_service import fetch_scripture_text_by_reference
            from theo.core.services.translation_service import get_translation_or_default

            telegram_id = call.from_user.id
            verses = get_saved_verses(telegram_id)

            if not verses:
                bot.answer_callback_query(
                    call.id,
                    "You have no saved verses yet. Tap Save on any verse to save it.",
                    show_alert=True,
                )
            else:
                record = container.group_repo.get_group(call.message.chat.id)
                translation = get_translation_or_default(
                    record.translation if record else None
                )

                sections = []
                for i, v in enumerate(verses, start=1):
                    book = v.get("book", "")
                    chapter = v.get("chapter", "")
                    verse = v.get("verse", "")
                    reference = f"{book} {chapter}:{verse}"

                    try:
                        verse_text = fetch_scripture_text_by_reference(
                            reference,
                            translation=translation,
                        )
                    except Exception:
                        verse_text = "Could not fetch verse text."

                    sections.append(
                        f"{i}. {reference} ({translation.upper()})\n{verse_text}"
                    )

                saved_text = "Your Saved Verses:\n\n" + "\n\n".join(sections)
                bot.answer_callback_query(call.id)
                bot.send_message(
                    call.message.chat.id,
                    saved_text,
                )

        elif action == "verse_history":
            bot.answer_callback_query(
                call.id,
                "Verse History feature coming soon!",
                show_alert=True
            )

        else:
            bot.answer_callback_query(call.id)


def _send_profile(bot: telebot.TeleBot, message: telebot.types.Message) -> None:
    telegram_id = message.from_user.id
    first_name = (message.from_user.first_name or "Friend").strip()

    user = get_user(telegram_id)

    if not user:
        bot.send_message(
            message.chat.id,
            "No profile found. Send /start to create your profile."
        )
        return

    translation = (user.get("translation") or "kjv").upper()
    tone = (user.get("tone_preference") or "warm").capitalize()
    member_since = str(user.get("created_at", ""))[:10]

    profile_text = (
        f"*Your Theo Profile*\n\n"
        f"*Name:* {first_name}\n"
        f"*Translation:* {translation}\n"
        f"*Tone:* {tone}\n"
        f"*Member Since:* {member_since}\n\n"
        f"Use the buttons below to manage your preferences."
    )

    bot.send_message(
        message.chat.id,
        profile_text,
        reply_markup=build_profile_inline_buttons(),
        parse_mode="Markdown"
    )