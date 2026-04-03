import logging
import telebot
from telebot.types import ChatMemberUpdated

from theo.app.container import Container
from theo.infra.db.repo import GroupRecord
from theo.adapters.telegram.views.keyboards import (
    build_category_picker_compact,
    build_category_picker_single_row,
)
from theo.core.services.verse_service import (
    get_votd_category,
    get_scripture_by_category,
    format_verse_message,
    list_categories,
)
from theo.infra.cache.memory_cache import first_time_cache

logger = logging.getLogger(__name__)


def register_autoregister(bot: telebot.TeleBot, container: Container) -> None:
    """
    Register handlers for:
    - Bot being added to group
    - Bot being mentioned/tagged
    - First-time user messages
    """
    repo = container.group_repo
    
    # Get bot username once at startup
    try:
        bot_me = bot.get_me()
        bot_username = bot_me.username
        logger.info(f"Bot username: @{bot_username}")
    except Exception as e:
        logger.warning(f"Could not get bot username: {e}")
        bot_username = "iamtheobot"  # Fallback

    @bot.my_chat_member_handler()
    def on_my_chat_member(update: ChatMemberUpdated) -> None:
        """Handle bot joining/leaving groups."""
        chat = update.chat
        chat_id = chat.id
        title = getattr(chat, "title", None)

        old_status = update.old_chat_member.status
        new_status = update.new_chat_member.status

        logger.info(f"my_chat_member: {old_status} -> {new_status} in {chat_id}")

        if new_status in ("member", "administrator") and old_status in ("left", "kicked"):
            # Bot joined group
            repo.upsert_group(GroupRecord(chat_id=chat_id, title=title, enabled=False))
            _send_group_welcome(bot, chat_id)

        if new_status in ("left", "kicked"):
            repo.disable_group(chat_id)

    @bot.message_handler(
        func=lambda message: is_bot_mentioned_without_command(message, bot_username),
        content_types=["text"]
    )
    def on_bot_mention(message: telebot.types.Message) -> None:
        """Handle bot being tagged/mentioned without a command."""
        user_id = message.from_user.id
        first_name = (message.from_user.first_name or "Friend").strip()
        
        is_first_time = first_time_cache.is_first_time(user_id)
        
        if is_first_time:
            _send_welcome_with_votd(bot, message, first_name)
        else:
            # Returning user in group
            intro_text = (
                f"Welcome back! 👋\n\n"
                f"I'm Theo, the community bot built for the YOUTHOPIA Bible Community.\n\n"
                f"I'm here to serve OUR COMMUNITY. I anchor us in daily scripture, foster spiritual connection, and keep us unified in Christ.\n\n"
                f"📖 *What would you like to explore?*"
            )
            bot.reply_to(
                message,
                intro_text,
                reply_markup=build_category_picker_compact(list_categories()),
                parse_mode="Markdown"
            )

    @bot.message_handler(
        func=lambda message: (
            not message.text.startswith("/") and
            message.chat.type == "private" and
            first_time_cache.is_first_time(message.from_user.id)
        ),
        content_types=["text"]
    )
    def on_first_dm(message: telebot.types.Message) -> None:
        """Handle first-time user sending a message in DM."""
        first_name = (message.from_user.first_name or "Friend").strip()
        _send_welcome_with_votd(bot, message, first_name)


def is_bot_mentioned_without_command(message: telebot.types.Message, bot_username: str) -> bool:
    """Check if bot was mentioned/tagged in message without a command."""
    text = getattr(message, "text", "") or ""
    
    # Skip if starts with command
    if text.startswith("/"):
        return False
    
    # Skip if no text
    if not text:
        return False
    
    # Check message entities for mentions
    entities = getattr(message, "entities", []) or []
    
    for entity in entities:
        # Check both mention and text_mention types
        if entity.type in ("mention", "text_mention"):
            start = entity.offset
            end = entity.offset + entity.length
            mentioned = text[start:end].lower()
            
            # Match if this mention is the bot
            if mentioned.lower() == f"@{bot_username.lower()}":
                logger.info(f"Bot mentioned: {mentioned}")
                return True
    
    return False


def _send_group_welcome(bot: telebot.TeleBot, chat_id: int) -> None:
    """Send welcome message when bot joins a group."""
    try:
        # Get today's VOTD
        votd_category = get_votd_category()
        verse_response = get_scripture_by_category(votd_category)
        
        welcome_text = (
            "� Hey YOUTHOPIA family! I'm Theo.\n\n"
            "I'm here to be the heartbeat of this group. Every morning at 6 AM, we'll receive a verse together. Our whole family—unified in scripture. Connected across the globe.\n\n"
            "Let's start with today:"
        )
        
        bot.send_message(chat_id, welcome_text, parse_mode="Markdown")
        
        # Send today's verse
        verse_message = format_verse_message(verse_response)
        bot.send_message(
            chat_id,
            verse_message,
            reply_markup=build_category_picker_compact(list_categories()),
            parse_mode="HTML",
        )

        # Send admin note
        admin_text = (
            "*Admins:* Enable daily verses with /enable_votd"
        )
        bot.send_message(chat_id, admin_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.exception("Failed to send group welcome")
        bot.send_message(
            chat_id,
            "Thanks for adding Theo! Use /help to get started."
        )


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
        
        # Build welcome message
        welcome_text = (
            f"👋 Welcome to Theo, {first_name}!\n\n"
            f"📖 *Here's today's verse to inspire you:*\n\n"
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
            "*Want verses every morning?*\n"
            "Use `/enable_votd` to get daily inspiration at 6 AM\n\n"
            "*Browse other scriptures:*\n"
            "Use `/faith`, `/love`, `/peace`, `/joy`, `/hope`, `/patience`, `/forgiveness`\n\n"
            "Need help? Use `/help`"
        )
        bot.send_message(message.chat.id, cta_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.exception("Failed to send welcome with VOTD")
        bot.send_message(
            message.chat.id,
            f"Hello {first_name}! Use /help for commands."
        )

