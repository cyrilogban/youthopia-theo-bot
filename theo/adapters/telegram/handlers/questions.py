import logging
import telebot
from theo.app.container import Container
from theo.infra.supabase_question_repo import (
    save_anonymous_question,
    get_question_asker,
    mark_question_answered
)

logger = logging.getLogger(__name__)

def register_questions(bot: telebot.TeleBot, container: Container) -> None:

    @bot.message_handler(func=lambda m: m.text == "Ask Anonymously")
    def on_ask_button(message: telebot.types.Message) -> None:
        if message.chat.id < 0:
            bot.reply_to(message, "This feature is only available in private DMs with Theo.")
            return

        msg = bot.send_message(
            message.chat.id,
            "🔒 *Anonymous Question Box*\n\n"
            "Use this to ask spiritual questions or share concerns.\n\n"
            "• Your identity is *hidden* from the community.\n"
            "• Your question will be posted in our official groups for discussion.\n"
            "• Leaders can reply to you privately and anonymously.\n\n"
            "*Please type your question below:*",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_question_submission, bot, container)

    def process_question_submission(message: telebot.types.Message, bot: telebot.TeleBot, container: Container) -> None:
        question_text = message.text
        if not question_text or question_text.startswith("/"):
            bot.send_message(message.chat.id, "❌ Cancelled. Please send a valid question text.")
            return

        user_id = message.from_user.id
        
        # 1. Save to DB
        question_id = save_anonymous_question(user_id, question_text)
        if not question_id:
            bot.send_message(message.chat.id, "❌ Sorry, something went wrong. Please try again later.")
            return

        # 2. Broadcast to Official Groups
        repo = container.group_repo
        subscribers = list(repo.list_enabled_groups())
        
        broadcast_text = (
            f"❓ *New Anonymous Question*\n"
            f"(Ref: #{question_id})\n\n"
            f"\"{question_text}\""
        )
        
        for sub in subscribers:
            if sub.chat_id < 0 and sub.is_official:
                try:
                    bot.send_message(sub.chat_id, broadcast_text, parse_mode="Markdown")
                except Exception as e:
                    logger.error(f"Failed to post anonymous question to group {sub.chat_id}: {e}")

        # 3. Notify Admin Privately
        admin_notify_text = (
            f"📩 *New Anonymous Question*\n"
            f"Question ID: #{question_id}\n\n"
            f"\"{question_text}\"\n\n"
            f"Use `/reply {question_id} <message>` to respond privately."
        )
        
        for admin_id in container.settings.admin_ids:
            try:
                bot.send_message(admin_id, admin_notify_text, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id} of new question: {e}")

        # 4. Confirm to User
        bot.send_message(
            message.chat.id,
            "✅ *Success!*\n\n"
            "Your question has been posted to the community and delivered to our leaders. "
            "Thank you for your vulnerability!",
            parse_mode="Markdown"
        )

    @bot.message_handler(commands=["reply"])
    def on_reply(message: telebot.types.Message) -> None:
        user_id = message.from_user.id
        if user_id not in container.settings.admin_ids:
            return

        # Format: /reply <id> <message>
        parts = message.text.split(None, 2)
        if len(parts) < 3:
            bot.reply_to(message, "Usage: /reply <ID> <your message>\nExample: /reply 105 I am praying for you!")
            return

        try:
            q_id = int(parts[1])
        except ValueError:
            bot.reply_to(message, "❌ Invalid Question ID.")
            return

        reply_content = parts[2]
        
        # 1. Get original asker
        asker_id = get_question_asker(q_id)
        if not asker_id:
            bot.reply_to(message, f"❌ Could not find an asker for Question #{q_id}.")
            return

        # 2. Send private DM to asker
        try:
            user_msg = (
                f"📩 *A Leader replied to your question (#{q_id}):*\n\n"
                f"\"{reply_content}\""
            )
            bot.send_message(asker_id, user_msg, parse_mode="Markdown")
            
            # 3. Mark as answered
            mark_question_answered(q_id)
            
            bot.reply_to(message, f"✅ Your reply to Question #{q_id} has been delivered privately.")
        except Exception as e:
            logger.error(f"Failed to deliver reply to user {asker_id}: {e}")
            bot.reply_to(message, "❌ Failed to deliver the message. The user might have blocked the bot.")
