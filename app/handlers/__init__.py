from config import ApplicationStates
from config import Callbacks
from config import DeclineUserStates
from handlers.admins import accept_user
from handlers.admins import decline_back_handler
from handlers.admins import decline_reason_hander
from handlers.admins import decline_user
from handlers.application import about
from handlers.application import activity
from handlers.application import game_mode
from handlers.application import old
from handlers.application import pubg_id
from handlers.application import start_command
from handlers.application import user_decision
from handlers.empty import unknown_handler
from telegram.ext import Application
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import filters
from telegram.ext import MessageHandler


def add_all_handlers(application: Application):
    """Регистрация всех обработчиков."""
    _add_conversation_handler(application)
    _add_admins_handler(application)
    application.add_handler(MessageHandler(filters.ALL, unknown_handler))
    # application.add_handler(CommandHandler(filters.ALL, decline_back_handler))


def _add_conversation_handler(application: Application):
    """Добавление обработчика FSM состояния заполнения анкеты."""
    conv_hander = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            ApplicationStates.pubgID_state: [MessageHandler(filters.TEXT, pubg_id)],
            ApplicationStates.old_state: [MessageHandler(filters.TEXT, old)],
            ApplicationStates.game_modes_state: [MessageHandler(filters.TEXT, game_mode)],
            ApplicationStates.activity_state: [MessageHandler(filters.TEXT, activity)],
            ApplicationStates.about_state: [
                MessageHandler(filters.Text(["Пропустить"]), about),
                MessageHandler(filters.TEXT, about),
            ],
            ApplicationStates.change_or_accept_state: [MessageHandler(filters.TEXT, user_decision)],
        },
        # TODO: Добавить хендлеры обработки ошибок (пользователь оправил некорректные данные)
        fallbacks=[MessageHandler(filters.ALL, unknown_handler)],
    )
    application.add_handler(conv_hander)


def _add_admins_handler(application: Application):
    """Добавление обработчика FSM состояния заполнения анкеты."""
    application.add_handler(
        CallbackQueryHandler(accept_user, pattern=f"^{Callbacks.APPLICATION_ACCEPT.value.split(':')[0]}")
    )
    conv_hander = ConversationHandler(
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
