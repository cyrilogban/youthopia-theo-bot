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

    @bot.message_handler(commands=["stats"])
    def on_stats(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        if user_id not in container.settings.admin_ids:
            return

        from theo.infra.supabase_user_repo import get_community_stats
        
        # 1. Get MongoDB stats (Groups & DMs)
        mongo_stats = container.group_repo.get_stats()
        
        # 2. Get Supabase stats (Users & Engagement)
        supabase_stats = get_community_stats()
        
        stats_text = (
            "📊 *Community Stats Summary*\n\n"
            "*Reach*\n"
            f"• Total Users: {supabase_stats['total_users']}\n"
            f"• Active DMs: {mongo_stats['active_dms']} / {mongo_stats['total_dms']}\n"
            f"• Active Groups: {mongo_stats['active_groups']} / {mongo_stats['total_groups']}\n\n"
            "*Engagement*\n"
            f"• Verses Sent (24h): {supabase_stats['verses_last_24h']}\n"
            f"• Total Saved Verses: {supabase_stats['total_saved_verses']}"
        )
        
        bot.send_message(message.chat.id, stats_text, parse_mode="Markdown")

    @bot.message_handler(commands=["addverse"])
    def on_addverse(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        if user_id not in container.settings.admin_ids:
            return

        # Expected format: /addverse <category> <reference>
        # e.g. /addverse hope John 3:16
        parts = message.text.split(None, 2)
        if len(parts) < 3:
            bot.reply_to(message, "Usage: /addverse <category> <book chapter:verse>\nExample: /addverse hope John 3:16")
            return

        category = parts[1].lower()
        reference_text = parts[2]

        from theo.core.services.reference_detection_service import parse_all_references
        from theo.infra.supabase_verse_repo import get_all_categories, add_verse_to_db

        # 1. Validate category
        valid_categories = get_all_categories()
        if category not in valid_categories:
            bot.reply_to(message, f"❌ Invalid category '{category}'.\nValid ones: {', '.join(valid_categories)}")
            return

        # 2. Parse reference
        refs = parse_all_references(reference_text)
        if not refs:
            bot.reply_to(message, f"❌ Could not parse reference: '{reference_text}'")
            return
        
        # Take the first reference found
        ref = refs[0]
        book = ref.book
        chapter = ref.chapter
        # Use start verse if it's a range
        verse = ref.verse_start

        # 3. Add to DB
        success = add_verse_to_db(category, book, chapter, verse)
        
        if success:
            bot.reply_to(message, f"✅ Successfully added *{book} {chapter}:{verse}* to the *{category}* category.", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Failed to add verse. It might already exist in the *{category}* category.", parse_mode="Markdown")
