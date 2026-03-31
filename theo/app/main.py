# theo/app/main.py
import logging
import time

"""
ARCHITECTURE NOTE â€“ Why I used this approach

There are two ways I could have written this scheduler logic.

OPTION 1:
I could have stored the Telegram bot inside container.py.

That would look like:

    class Container:
        settings
        group_repo
        bot

And build_container() would receive and return the bot.
Then in schedule_service.py I would do:

    bot = container.bot

In that case, the Container is responsible for holding
the Telegram bot instance.

I did NOT choose this method because it ties the Container
directly to TeleBot.

---------------------------------------------------------

OPTION 2 (what I chose):

I removed `bot: TeleBot` from container.py.
My Container now only holds:
    - settings
    - group_repo

In main.py, I create the bot separately:

    bot = create_bot(settings)

Then I pass it into the scheduler:

    start_scheduler(lambda: daily_job(container, bot))

In schedule_service.py, the function receives:

    daily_job(container, bot)

So the container handles database logic,
and the bot handles sending messages.

---------------------------------------------------------

Why I chose this:

I want container.py to stay focused only on infrastructure
(settings + database). I donâ€™t want it tied to Telegram.

If I change the Telegram library tomorrow
(TeleBot â†’ something else),
I only need to update:
    - adapters/telegram/*
    - main.py
    - schedule_service.py

I wonâ€™t have to rewrite my container or database logic.

Thatâ€™s why I chose this approach. More information on this is found in ARCHITECTURE.MD
"""


import telebot

from theo.app.config import load_settings
from theo.app.logging_setup import setup_logging
from theo.app.container import build_container

from theo.adapters.telegram.bot import create_bot
from theo.adapters.telegram.router import register_routes

from theo.infra.scheduler.aps import start_scheduler
from theo.core.services.schedule_service import daily_job
from theo.app.keep_alive import keep_alive

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    settings = load_settings()

    # Option A: container does NOT store the bot
    container = build_container(settings)

    # bot is created separately
    bot = create_bot(settings)

    # Set command menu
    try:
        commands = [
            telebot.types.BotCommand("start", "Begin using Theo"),
            telebot.types.BotCommand("verse", "Get a scripture"),
            telebot.types.BotCommand("status", "Check subscription status"),
            telebot.types.BotCommand("enable_votd", "Enable daily verses"),
            telebot.types.BotCommand("disable_votd", "Stop daily verses"),
            telebot.types.BotCommand("translation", "Change Bible version"),
            telebot.types.BotCommand("help", "Show all commands"),
        ]
        bot.set_my_commands(commands)
        logger.info("Bot commands menu updated successfully.")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")

    register_routes(bot, container)

    # scheduler job receives bot as an argument
    start_scheduler(lambda: daily_job(container, bot))

    logger.info("Theo v2 starting polling...")

    while True:
        try:
            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                allowed_updates=["message", "callback_query", "my_chat_member", "chat_member"],
            )
        except Exception as e:
            logger.exception(f"Polling crashed: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
