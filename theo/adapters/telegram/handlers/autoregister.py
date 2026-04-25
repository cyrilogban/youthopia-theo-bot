import logging
import telebot
from telebot.types import ChatMemberUpdated

from theo.app.container import Container
from theo.infra.db.repo import GroupRecord
from theo.adapters.telegram.views.keyboards import build_verse_actions_keyboard
from theo.core.services.verse_service import (
    get_votd_category,
    format_verse_message,
    VerseLookupError,
    VerseReference,
    VerseResponse,
    fetch_scripture_text_by_reference,
)
from theo.core.services.translation_service import get_translation_or_default
from theo.infra.supabase_user_repo import get_or_create_user

logger = logging.getLogger(__name__)


def register_autoregister(bot: telebot.TeleBot, container: Container) -> None:
    repo = container.group_repo

    try:
        bot_me = bot.get_me()
        bot_username = bot_me.username
        logger.info(f"Bot username: @{bot_username}")
    except Exception as e:
        logger.warning(f"Could not get bot username: {e}")
        bot_username = "iamtheobot"

    @bot.my_chat_member_handler()
    def on_my_chat_member(update: ChatMemberUpdated) -> None:
        chat = update.chat
        chat_id = chat.id
        title = getattr(chat, "title", None)
        old_status = update.old_chat_member.status
        new_status = update.new_chat_member.status

        logger.info(f"my_chat_member: {old_status} -> {new_status} in {chat_id}")

        if new_status in ("member", "administrator") and old_status in ("left", "kicked"):
            repo.upsert_group(GroupRecord(chat_id=chat_id, title=title, enabled=False))
            _send_group_welcome(bot, chat_id)

        if new_status in ("left", "kicked"):
            repo.disable_group(chat_id)

    @bot.message_handler(
        func=lambda message: is_bot_mentioned_without_command(message, bot_username),
        content_types=["text"]
    )
    def on_bot_mention(message: telebot.types.Message) -> None:
        first_name = (message.from_user.first_name or "Friend").strip()
        username = getattr(message.from_user, "username", None)
        telegram_id = message.from_user.id

        user, is_new = get_or_create_user(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
        )

        if is_new:
            _send_welcome_with_votd(bot, message, first_name)
        else:
            intro_text = (
                f"Welcome back, {first_name}! 👋\n\n"
                f"I'm Theo, your scripture companion built for the YOUTHOPIA Bible Community.\n\n"
                f"Every morning at 6 AM you'll get a verse to start your day grounded in God's word.\n\n"
                f"Use /enable_votd to subscribe or /help for more options."
            )
            bot.reply_to(message, intro_text)


def is_bot_mentioned_without_command(message: telebot.types.Message, bot_username: str) -> bool:
    text = getattr(message, "text", "") or ""
    if text.startswith("/"):
        return False
    if not text:
        return False
    entities = getattr(message, "entities", []) or []
    for entity in entities:
        if entity.type in ("mention", "text_mention"):
            start = entity.offset
            end = entity.offset + entity.length
            mentioned = text[start:end].lower()
            if mentioned.lower() == f"@{bot_username.lower()}":
                return True
    return False


def _get_votd_verse_response() -> VerseResponse:
    """Get today's VOTD through rotation logic."""
    from theo.infra.supabase_verse_repo import get_votd_verse
    votd = get_votd_verse()
    if not votd:
        raise VerseLookupError("Could not get VOTD verse.")
    reference = VerseReference(
        book=votd["book"],
        chapter=votd["chapter"],
        verse=votd["verse"],
    )
    votd_category = get_votd_category()
    normalized_translation = get_translation_or_default(None)
    verse_text = fetch_scripture_text_by_reference(
        reference.reference,
        translation=normalized_translation
    )
    return VerseResponse(
        category=votd_category,
        reference=reference,
        text=verse_text,
        translation=normalized_translation,
    )


def _send_group_welcome(bot: telebot.TeleBot, chat_id: int) -> None:
    try:
        verse_response = _get_votd_verse_response()

        welcome_text = (
            "👋 Hey YOUTHOPIA family! I'm Theo.\n\n"
            "I'm here to anchor this group in daily scripture. Every morning at 6 AM, we receive a verse together.\n\n"
            "Here's today's verse:"
        )
        bot.send_message(chat_id, welcome_text)

        verse_message = format_verse_message(verse_response)
        bot.send_message(
            chat_id,
            verse_message,
            reply_markup=build_verse_actions_keyboard(
                verse_response.category,
                verse_response.reference.reference,
            ),
            parse_mode="HTML",
        )

        bot.send_message(
            chat_id,
            "*Admins:* Enable daily verses with /enable_votd",
            parse_mode="Markdown"
        )

    except Exception:
        logger.exception("Failed to send group welcome")
        bot.send_message(chat_id, "Thanks for adding Theo! Use /help to get started.")


def _send_welcome_with_votd(
    bot: telebot.TeleBot,
    message: telebot.types.Message,
    first_name: str
) -> None:
    try:
        verse_response = _get_votd_verse_response()

        welcome_text = (
            f"🌐 Welcome to the YOUTHOPIA family, {first_name}.\n\n"
            f"I'm Theo. I exist because this community matters.\n\n"
            f"Every morning at 6 AM, I deliver a verse to our entire family. "
            f"We all see it together. We all start our day grounded in the same truth. "
            f"That's the power of what we're building - a digital sanctuary where nobody walks alone.\n\n"
            f"Here's today's anchor verse:"
        )
        bot.send_message(message.chat.id, welcome_text)

        verse_message = format_verse_message(verse_response)
        bot.send_message(
            message.chat.id,
            verse_message,
            reply_markup=build_verse_actions_keyboard(
                verse_response.category,
                verse_response.reference.reference,
            ),
            parse_mode="HTML",
        )

        cta_text = (
            "*Want verses every morning?*\n"
            "Use /enable_votd to get daily inspiration at 6 AM\n\n"
            "Need help? Use /help"
        )
        bot.send_message(message.chat.id, cta_text, parse_mode="Markdown")

    except Exception:
        logger.exception("Failed to send welcome with VOTD")
        bot.send_message(
            message.chat.id,
            f"Hello {first_name}! Use /help for commands."
        )