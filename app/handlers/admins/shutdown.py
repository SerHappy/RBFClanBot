from telegram import Update
from telegram.ext import ContextTypes

from app.core.config import settings


async def shutdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shutdown the bot."""
    if not update.effective_user:
        return
    if update.effective_user.id != settings.DEVELOPER_CHAT_ID:
        return
    context.application.stop_running()
