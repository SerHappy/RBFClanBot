from .new_user import new_user_handler
from telegram.ext import Application
from telegram.ext import filters
from telegram.ext import MessageHandler


def register_chat_handlers(application: Application) -> None:
    """Добавление обработчиков для чата."""
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_user_handler))
