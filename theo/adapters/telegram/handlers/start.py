import logging
import telebot

from theo.app.container import Container
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


def register_start(bot: telebot.TeleBot, container: Container | None = None) -> None:
    @bot.message_handler(commands=["start"])
    def _start(message: telebot.types.Message) -> None:
        first_name = (message.from_user.first_name or "Friend").strip()
        username = getattr(message.from_user, "username", None)
        telegram_id = message.from_user.id

        # Check Supabase if user exists or create them
        user, is_new = get_or_create_user(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
        )

        if is_new:
            _send_welcome_with_votd(bot, message, first_name)
        else:
            _send_simple_welcome(bot, message, first_name)


def _send_welcome_with_votd(
    bot: telebot.TeleBot,
    message: telebot.types.Message,
    first_name: str
) -> None:
    """Send welcome message with today's VOTD for new users."""
    try:
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
        verse_response = VerseResponse(
            category=votd_category,
            reference=reference,
            text=verse_text,
            translation=normalized_translation,
        )

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

        from theo.adapters.telegram.views.keyboards import build_main_menu_keyboard
        
        cta_text = (
            "*Want verses every morning?*\n"
            "Use /enable_votd to get daily inspiration at 6 AM\n\n"
            "Need help? Use /help"
        )
        bot.send_message(
            message.chat.id,
            cta_text,
            reply_markup=build_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    except Exception:
        logger.exception("Failed to send welcome with VOTD")
        _send_simple_welcome(bot, message, first_name)


def _send_simple_welcome(
    bot: telebot.TeleBot,
    message: telebot.types.Message,
    first_name: str
) -> None:
    from theo.adapters.telegram.views.keyboards import build_main_menu_keyboard
    text = (
        f"Welcome back, {first_name}! 👋\n\n"
        f"I'm Theo, your scripture companion built for the YOUTHOPIA Bible Community.\n\n"
        f"Every morning at 6 AM you'll get a verse to start your day grounded in God's word.\n\n"
        f"Use /enable_votd to subscribe or /help for more options."
    )
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=build_main_menu_keyboard()
    )
