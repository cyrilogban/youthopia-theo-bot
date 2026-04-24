import telebot

def register_start(bot: telebot.TeleBot, container) -> None:
    @bot.message_handler(commands=["start"])
    def start(message: telebot.types.Message) -> None:
        # TODO: Add your start logic here
        bot.send_message(
            message.chat.id,
            "Hello! I am your bot."
        )
