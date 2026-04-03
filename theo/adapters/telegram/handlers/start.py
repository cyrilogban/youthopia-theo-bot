import logging
import telebot

from theo.app.container import Container
from theo.adapters.telegram.views.keyboards import (
    build_category_picker_compact,
    build_help_button_keyboard,
)
from theo.core.services.verse_service import (
    get_votd_category,
    get_scripture_by_category,
    format_verse_message,
    list_categories,
)
from theo.infra.cache.memory_cache import first_time_cache

logger = logging.getLogger(__name__)


def register_start(bot: telebot.TeleBot, container: Container | None = None) -> None:
    @bot.message_handler(commands=["start"])
    def _start(message: telebot.types.Message) -> None:
        first_name = (message.from_user.first_name or "Friend").strip()
        user_id = message.from_user.id
        
        # Check if first time
        is_first_time = first_time_cache.is_first_time(user_id)
        
        if is_first_time:
            _send_welcome_with_votd(bot, message, first_name)
        else:
            _send_simple_welcome(bot, message, first_name)


def _send_welcome_with_votd(
    bot: telebot.TeleBot,
    message: telebot.types.Message,
    first_name: str
) -> None:
    """Send welcome message with today's VOTD and category picker."""
    try:
        # Get today's VOTD
        votd_category = get_votd_category()
        verse_response = get_scripture_by_category(votd_category)
        
        # Build welcome message - Community-First variation
        welcome_text = (
            f"🌐 Welcome to the YOUTHOPIA family, {first_name}.\n\n"
            f"I'm Theo. I exist because this community matters.\n\n"
            f"Every morning at 6 AM, I deliver a verse to our entire family. We all see it together. We all start our day grounded in the same truth. That's the power of what we're building—a digital sanctuary where nobody walks alone.\n\n"
            f"*Here's today's anchor verse:*\n\n"
        )
        
        bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
        
        # Send the verse
        verse_message = format_verse_message(verse_response)
        bot.send_message(
            message.chat.id,
            verse_message,
            reply_markup=build_category_picker_compact(list_categories()),
            parse_mode="HTML",
        )

        # Send call-to-action
        cta_text = (
            "Want to explore more? Pick a theme above."
        )
        bot.send_message(message.chat.id, cta_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.exception("Failed to send welcome with VOTD")
        _send_simple_welcome(bot, message, first_name)


def _send_simple_welcome(
    bot: telebot.TeleBot,
    message: telebot.types.Message,
    first_name: str
) -> None:
    """Send welcome message for returning users (not first time)."""
    text = (
        f"Welcome back! 👋\n\n"
        f"I'm Theo, the community bot built for the YOUTHOPIA Bible Community.\n\n"
        f"I'm here to serve YOU on your faith journey. Every morning at 6 AM, you'll get a verse. Browse scripture by category. Change translations. Explore the Word at your pace.\n\n"
        f"📖 *What would you like to explore today?*"
    )
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=build_category_picker_compact(list_categories()),
        parse_mode="Markdown"
    )

