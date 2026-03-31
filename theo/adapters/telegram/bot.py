import telebot
from theo.app.config import Settings

def create_bot(settings: Settings) -> telebot.TeleBot:
    return telebot.TeleBot(settings.bot_token, parse_mode=None )
    