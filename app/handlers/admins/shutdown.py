from telegram import Update
from telegram.ext import ContextTypes

from app.core.config import settings


async def shutdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle bot shutdown.

    Args:
        update (Update): The update.
        context (ContextTypes.DEFAULT_TYPE): The context.

    Returns:
        None
    """
    if not update.effective_user:
        return
    if update.effective_user.id != settings.DEVELOPER_CHAT_ID:
        return
    context.application.stop_running()
