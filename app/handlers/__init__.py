from handlers.application import register_application_handlers
from config import Callbacks
from config import DeclineUserStates
from handlers.admins import accept_user
from handlers.admins import decline_back_handler
from handlers.admins import decline_reason_hander
from handlers.admins import decline_user
from handlers.empty import unknown_handler
from telegram.ext import Application
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram.ext import filters
from telegram.ext import MessageHandler


def add_all_handlers(application: Application):
    """Регистрация всех обработчиков."""
    register_application_handlers(application)
    _add_admins_handler(application)
    application.add_handler(MessageHandler(filters.ALL, unknown_handler))


def _add_admins_handler(application: Application):
    """Добавление обработчика FSM состояния заполнения анкеты."""
    application.add_handler(
        CallbackQueryHandler(accept_user, pattern=f"^{Callbacks.APPLICATION_ACCEPT.value.split(':')[0]}")
    )
    conv_hander = ConversationHandler(
        per_user=False,
        entry_points=[
            CallbackQueryHandler(decline_user, pattern=f"^{Callbacks.APPLICATION_DECLINE.value.split(':')[0]}"),
        ],
        states={
            DeclineUserStates.decline_reason_state: [
                CallbackQueryHandler(
                    decline_back_handler,
                    pattern=f"^{Callbacks.APPLICATION_DECLINE_BACK.value}",
                ),
                MessageHandler(
                    filters.TEXT,
                    decline_reason_hander,
                ),
            ]
        },
        fallbacks=[],
    )

    application.add_handler(conv_hander)
