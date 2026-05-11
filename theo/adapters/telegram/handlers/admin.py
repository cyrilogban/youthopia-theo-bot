import logging
import telebot
from theo.app.container import Container

logger = logging.getLogger(__name__)

def register_admin(bot: telebot.TeleBot, container: Container) -> None:
    
    @bot.message_handler(commands=["broadcast"])
    def on_broadcast(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        
        # Admin check
        if user_id not in container.settings.admin_ids:
            logger.warning(f"Unauthorized broadcast attempt from user_id: {user_id}")
            return

        # Extract broadcast text
        text = message.text.split(None, 1)
        if len(text) < 2:
            bot.reply_to(message, "Usage: /broadcast <your message>")
            return
        
        broadcast_content = text[1]
        
        # Get all subscribed entities (groups and private chats)
        repo = container.group_repo
        subscribers = list(repo.list_enabled_groups())
        
        if not subscribers:
            bot.reply_to(message, "No active subscribers found to broadcast to.")
            return

        sent_count = 0
        fail_count = 0
        
        status_msg = bot.reply_to(message, f"🚀 Starting broadcast to {len(subscribers)} subscribers...")

        for sub in subscribers:
            try:
                bot.send_message(sub.chat_id, broadcast_content)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send broadcast to {sub.chat_id}: {e}")
                fail_count += 1
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"✅ Broadcast complete!\n\nSuccessfully sent to: {sent_count}\nFailed: {fail_count}"
        )
