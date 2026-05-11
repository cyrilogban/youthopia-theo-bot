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
                # GATEKEEPER LOGIC:
                # 1. Always allow Private DMs (chat_id > 0)
                # 2. Only allow Groups (chat_id < 0) if they are marked as 'is_official'
                is_private_dm = sub.chat_id > 0
                if not is_private_dm and not sub.is_official:
                    logger.info(f"Skipping broadcast to unauthorized group: {sub.chat_id}")
                    continue

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

    @bot.message_handler(commands=["whitelist"])
    def on_whitelist(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        if user_id not in container.settings.admin_ids:
            return

        chat_id = message.chat.id
        if chat_id > 0:
            bot.reply_to(message, "This command can only be used in groups.")
            return

        repo = container.group_repo
        repo.set_group_official_status(chat_id, True)
        bot.reply_to(message, "✅ This group is now whitelisted for official broadcasts.")

    @bot.message_handler(commands=["unwhitelist"])
    def on_unwhitelist(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        if user_id not in container.settings.admin_ids:
            return

        chat_id = message.chat.id
        if chat_id > 0:
            bot.reply_to(message, "This command can only be used in groups.")
            return

        repo = container.group_repo
        repo.set_group_official_status(chat_id, False)
        bot.reply_to(message, "❌ This group has been removed from official broadcasts.")
