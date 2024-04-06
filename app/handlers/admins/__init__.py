from .accept import accept_application
from .ban import ban_user_preprocess
from .reject import reject_application_start
from .reject import reject_back_button_handler
from .reject import reject_reason_hander
from .unban import unban_user_preprocess
from config import Callbacks
from config import DeclineUserStates
from telegram.ext import Application
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import filters
from telegram.ext import MessageHandler


def register_admin_handlers(application: Application):
    """Добавление обработчика FSM состояния заполнения анкеты."""
    application.add_handler(
        CallbackQueryHandler(accept_application, pattern=f"^{Callbacks.APPLICATION_ACCEPT.value.split(':')[0]}")
    )
    conv_hander = ConversationHandler(
        per_user=False,
        entry_points=[
            CallbackQueryHandler(
                reject_application_start, pattern=f"^{Callbacks.APPLICATION_DECLINE.value.split(':')[0]}"
            ),
        ],
        states={
            DeclineUserStates.decline_reason_state: [
                CallbackQueryHandler(
                    reject_back_button_handler,
                    pattern=f"^{Callbacks.APPLICATION_DECLINE_BACK.value}",
                ),
                MessageHandler(
                    filters.TEXT,
                    reject_reason_hander,
                ),
            ]
        },
        fallbacks=[],
    )

    application.add_handler(conv_hander)
    application.add_handler(CommandHandler(command="ban", callback=ban_user_preprocess, has_args=1))
    application.add_handler(CommandHandler(command="unban", callback=unban_user_preprocess, has_args=1))
