import telebot

def register_help(bot: telebot.TeleBot, container) -> None:
    @bot.message_handler(commands=["help"])
    def help(message: telebot.types.Message) -> None:
        # TODO: Add your help text here
        bot.send_message(
            message.chat.id,
            "Here are the available commands:\n/start - Start the bot\n/help - Show this message"
        )
