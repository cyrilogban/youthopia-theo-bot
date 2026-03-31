from telebot import TeleBot
from telebot.types import Message


def is_chat_admin(bot: TeleBot, message: Message) -> bool:
    """
    Returns True if the message sender is an admin/creator of the chat.
    Works for groups/supergroups.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = bot.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "creator")