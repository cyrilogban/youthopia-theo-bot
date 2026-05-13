import telebot



from theo.app.container import Container

def register_help(bot: telebot.TeleBot, container: Container) -> None:
    @bot.message_handler(commands=["help"])
    def _help(message: telebot.types.Message) -> None:
        from theo.adapters.telegram.views.keyboards import (
            build_user_main_menu_keyboard,
            build_admin_main_menu_keyboard
        )
        
        is_admin = message.from_user.id in container.settings.admin_ids
        keyboard = build_admin_main_menu_keyboard() if is_admin else build_user_main_menu_keyboard()

        bot.reply_to(
            message,
            "Commands:\n"
            "/start - Welcome & Setup\n"
            "/profile - My Profile\n"
            "/status - Subscription Status\n"
            "/enable_votd - Daily Verse ON\n"
            "/disable_votd - Daily Verse OFF\n"
            "/translation - Bible Translation\n"
            "/help - Help & Support",
            reply_markup=keyboard
        )
