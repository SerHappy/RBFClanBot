from telegram.ext import Application, MessageHandler, filters

from app.handlers.chat.new_user_joined import new_user_joined_handler


def register_chat_handlers(application: Application) -> None:
    """
    Register chat handlers.

    Args:
        application (Application): The application.

    Returns:
        None
    """
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_user_joined_handler),
    )
