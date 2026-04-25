from telebot import TeleBot

from theo.app.container import Container
from theo.adapters.telegram.handlers.start import register_start
from theo.adapters.telegram.handlers.help import register_help
from theo.adapters.telegram.handlers.groups import register_groups
from theo.adapters.telegram.handlers.autoregister import register_autoregister
from theo.adapters.telegram.handlers.autodetect import register_autodetect
from theo.adapters.telegram.handlers.verse import register_verse
from theo.adapters.telegram.handlers.profile import register_profile


def register_routes(bot: TeleBot, container: Container) -> None:
    register_start(bot, container)
    register_help(bot)
    register_groups(bot, container)
    register_autoregister(bot, container)
    register_profile(bot, container)
    register_verse(bot, container)
    register_autodetect(bot, container)