from .finish import user_decision
from .questions import about
from .questions import activity
from .questions import age
from .questions import game_mode
from .questions import pubg_id
from .start import start_command
from config import ApplicationStates
from handlers.empty import unknown_handler
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import filters
from telegram.ext import MessageHandler


def register_application_handlers(application: Application):
    """Добавление обработчика FSM состояния заполнения анкеты."""
    conv_hander = ConversationHandler(
        entry_points=[CommandHandler("start", start_command.start_command)],
        states={
            ApplicationStates.pubgID_state: [MessageHandler(filters.TEXT, pubg_id.pubg_id)],
            ApplicationStates.age_state: [MessageHandler(filters.TEXT, age.age)],
            ApplicationStates.game_modes_state: [MessageHandler(filters.TEXT, game_mode.game_mode)],
            ApplicationStates.activity_state: [MessageHandler(filters.TEXT, activity.activity)],
            ApplicationStates.about_state: [
                MessageHandler(filters.Text(["Пропустить"]), about.about_skip),
                MessageHandler(filters.TEXT, about.about),
            ],
            ApplicationStates.change_or_accept_state: [MessageHandler(filters.TEXT, user_decision.user_decision)],
        },
        # TODO: Добавить хендлеры обработки ошибок (пользователь оправил некорректные данные)
        fallbacks=[MessageHandler(filters.ALL, unknown_handler)],
    )
    application.add_handler(conv_hander)
