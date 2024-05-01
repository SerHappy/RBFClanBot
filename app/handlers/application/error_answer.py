from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes


async def fallback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """
    Handle unknown answer.

    Args:
        update: The update.
        context: The context.

    Returns:
        None
    """
    chat = update.effective_chat
    if not chat:
        logger.critical(
            (
                "Чат не определен при вызове коллбека! "
                "Данная ошибка не должна никогда происходить."
            ),
        )
        return
    if chat.type != "private":
        return
    await chat.send_message(
        (
            "Неверный формат ответа.\n"
            "Если ошибка повторяется, обратитесь к менеджеру @RBFManager."
        ),
    )
