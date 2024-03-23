from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes


async def unknown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown command."""
    chat = update.effective_chat
    if not chat:
        logger.critical("Чат не определен при вызове коллбека! Данная ошибка не должна никогда происходить.")
        return
    await chat.send_message(
        "Неизвестный текст или команда. Если вы считаете, что это ошибка, обратитесь к разработчику @SerHappy"
    )
