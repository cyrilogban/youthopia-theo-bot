from telebot import TeleBot

from theo.app.container import Container
from theo.adapters.telegram.handlers.start import register_start
from theo.adapters.telegram.handlers.help import register_help
from theo.adapters.telegram.handlers.groups import register_groups
from theo.adapters.telegram.handlers.autoregister import register_autoregister
from theo.adapters.telegram.handlers.autodetect import register_autodetect
from theo.adapters.telegram.handlers.verse import register_verse
from theo.adapters.telegram.handlers.profile import register_profile
from theo.adapters.telegram.handlers.admin import register_admin
from theo.adapters.telegram.handlers.questions import register_questions


def register_routes(bot: TeleBot, container: Container) -> None:
    # 1. High-priority specialized handlers (Buttons & Admin)
    register_admin(bot, container)
    register_questions(bot, container)
    register_profile(bot, container)

    # 2. Command & Interaction handlers
    register_start(bot, container)
    register_help(bot)
    register_groups(bot, container)
    register_verse(bot, container)

    # 3. Dynamic text detection (Catch-all logic last)
    register_autodetect(bot, container)
    register_autoregister(bot, container)