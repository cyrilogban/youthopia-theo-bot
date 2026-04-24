from telebot import TeleBot
from telebot.types import Message


def is_chat_admin(bot: TeleBot, message: Message) -> bool:
    """
    Returns True if the message sender is an admin/creator of the chat.
    Works for groups, supergroups, and channel discussion groups.
    """
    try:
        chat_id = message.chat.id
        user = message.from_user

        # In channel discussion groups from_user can be None
        if user is None:
            return False

        user_id = user.id

        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        # If we cannot determine admin status, deny by default
        return False