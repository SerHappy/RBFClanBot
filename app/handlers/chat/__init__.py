from telegram.ext import Application, MessageHandler, filters

from .new_user import new_user_handler


def register_chat_handlers(application: Application) -> None:
    """Добавление обработчиков для чата."""
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_user_handler))
