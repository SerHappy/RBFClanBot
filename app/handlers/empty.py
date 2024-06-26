from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes


async def unknown_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """
    Handle unknown command.

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
    logger.info(f"Получена неизвестная команда в чате chat_id={chat.id}.")
    await chat.send_message(
        (
            "Неизвестный текст или команда.\n"
            "Попробуйте перезапустить заполнение заявки, вызвав команду /start.\n"
            "Если ошибка повторяется, обратитесь к менеджеру @RBFManager."
        ),
    )
