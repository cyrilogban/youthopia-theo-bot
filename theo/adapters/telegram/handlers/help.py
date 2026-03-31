import telebot



def register_help(bot: telebot.TeleBot) -> None:
    @bot.message_handler(commands=["help"])
    def _help(message: telebot.types.Message) -> None:
        bot.reply_to(
            message,
            "Commands:\n"
            "/start - check if Theo is alive\n"
            "/help - show this message\n"
            "/verse - choose a scripture category\n"
            "/translation [kjv|web|bbe|asv] - view or change translation\n"
            "/enable_votd - enable daily Verse of the Day in this chat\n"
            "/disable_votd - disable daily Verse of the Day in this chat\n"
            "/status - check VOTD status in this chat\n"
        )
