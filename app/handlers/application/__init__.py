from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.handlers.application.error_answer import fallback_handler
from app.handlers.application.finish import user_decision
from app.handlers.application.questions import about, activity, age, game_mode, pubg_id
from app.handlers.application.start import start_command
from app.handlers.config import ApplicationStates


def register_application_handlers(application: Application) -> None:
    """
    Register application handlers.

    Args:
        application (Application): The application.

    Returns:
        None
    """
    conv_hander = ConversationHandler(
        entry_points=[CommandHandler("start", start_command.start_command)],
        states={
            ApplicationStates.PUBG_ID_STATE.value: [
                MessageHandler(filters.TEXT, pubg_id.pubg_id),
            ],
            ApplicationStates.AGE_STATE.value: [MessageHandler(filters.TEXT, age.age)],
            ApplicationStates.GAME_MODES_STATE.value: [
                MessageHandler(filters.TEXT, game_mode.game_mode),
            ],
            ApplicationStates.ACTIVITY_STATE.value: [
                MessageHandler(filters.TEXT, activity.activity),
            ],
            ApplicationStates.ABOUT_STATE.value: [
                MessageHandler(filters.Text(["Пропустить"]), about.about_skip),
                MessageHandler(filters.TEXT, about.about),
            ],
            ApplicationStates.CHANGE_OR_ACCEPT_STATE: [
                MessageHandler(filters.TEXT, user_decision.user_decision),
            ],
        },
        # TODO: Добавить хендлеры обработки ошибок
        # (пользователь оправил некорректные данные)
        fallbacks=[MessageHandler(filters.ALL, fallback_handler)],
    )
    application.add_handler(conv_hander)
