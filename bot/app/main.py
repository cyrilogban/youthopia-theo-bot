from bot.app.config import Settings
from bot.app.container import build_container

def main():
    settings = Settings()
    container = build_container(settings)

    # TODO: Create your bot here
    # bot = telebot.TeleBot(settings.bot_token)

    # TODO: Register your routes here
    # from bot.adapters.telegram.router import register_routes
    # register_routes(bot, container)

    # TODO: Start your scheduler here
    # from bot.infra.scheduler.setup import start_scheduler
    # start_scheduler()

    # TODO: Start keep-alive server here
    # from bot.infra.http.keep_alive import start_keep_alive
    # start_keep_alive()

    # TODO: Start polling
    # bot.infinity_polling()

if __name__ == "__main__":
    main()
