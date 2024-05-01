import json
import os
import traceback
from pathlib import Path

import aiofiles
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from app.core.config import settings


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle all uncaught exceptions.

    Args:
        update (object): The update.
        context (ContextTypes.DEFAULT_TYPE): The context.

    Returns:
        None
    """
    logger.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None,
        context.error,
        context.error.__traceback__,  # type: ignore[attr-defined]
    )
    tb_string = "".join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    temp_file_path = f"temp_error_{os.urandom(4).hex()}.txt"
    async with aiofiles.open(temp_file_path, mode="w", encoding="utf-8") as tmp_file:
        await tmp_file.write("An exception was raised while handling an update\n")
        await tmp_file.write(
            f"update = {json.dumps(update_str, indent=2, ensure_ascii=False)}\n\n",
        )
        await tmp_file.write(f"context.chat_data = {context.chat_data!s}\n\n")
        await tmp_file.write(f"context.user_data = {context.user_data!s}\n\n")
        await tmp_file.write(tb_string + "\n")

    async with aiofiles.open(temp_file_path, mode="rb") as doc_file:
        file_content = await doc_file.read()
        await context.bot.send_document(
            chat_id=settings.DEVELOPER_CHAT_ID,
            document=file_content,
            filename=Path(temp_file_path).name,
            caption="An exception was raised while handling an update.",
        )

    Path(temp_file_path).unlink()
