from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.core.config import settings
from app.handlers.admins.applications.accept import accept_application
from app.handlers.admins.applications.reject import (
    reject_application_start,
    reject_back_button_handler,
    reject_reason_hander,
    reject_without_reason_hander,
)
from app.handlers.admins.applications.take import take_application_handler
from app.handlers.admins.shutdown import shutdown_handler
from app.handlers.admins.users.ban import ban_user
from app.handlers.admins.users.unban import unban_user
from app.handlers.config import Callbacks, DeclineUserStates


# TODO: Разнести по __init__ файлам
def register_admin_handlers(application: Application) -> None:
    """Добавление обработчика FSM состояния заполнения анкеты."""
    application.add_handler(
        CallbackQueryHandler(
            accept_application,
            pattern=f"^{Callbacks.APPLICATION_ACCEPT.value.split(':')[0]}",
        ),
    )
    application.add_handler(
        CallbackQueryHandler(
            take_application_handler,
            pattern=f"^{Callbacks.APPLICATION_HANDLE.value.split(':')[0]}",
        ),
    )
    conv_hander = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                reject_application_start,
                pattern=f"^{Callbacks.APPLICATION_DECLINE.value.split(':')[0]}",
            ),
        ],
        states={
            DeclineUserStates.DECLINE_REASON_STATE: [
                CallbackQueryHandler(
                    reject_back_button_handler,
                    pattern=f"^{Callbacks.APPLICATION_DECLINE_BACK.value}",
                ),
                CallbackQueryHandler(
                    reject_without_reason_hander,
                    pattern=f"^{Callbacks.APPLICATION_DECLINE_WITHOUT_REASON.value.split(':')[0]}",
                ),
                MessageHandler(
                    filters.TEXT,
                    reject_reason_hander,
                ),
            ],
        },
        fallbacks=[],
    )

    application.add_handler(conv_hander)
    application.add_handler(
        CommandHandler(command="ban", callback=ban_user, has_args=1),
    )
    application.add_handler(
        CommandHandler(command="unban", callback=unban_user, has_args=1),
    )
    application.add_handler(
        CommandHandler(
            command="shutdown",
            callback=shutdown_handler,
            filters=filters.User(settings.DEVELOPER_CHAT_ID),
        ),
    )
