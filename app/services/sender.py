from db import Database
from db import Session
from decouple import config
from loguru import logger
from telegram import Bot
from utils import application_format

import keyboards


async def send_application_to_admins(bot: Bot, user_id: int) -> None:
    """Send application to admins."""
    admin_chat = config("ADMIN_CHAT_ID", cast=int)
    logger.debug(f"Отправка заявки пользователя<id={user_id}> админам в чат <id={admin_chat}>.")
    async with Session() as session:
        db = Database(session)
        application = await db.application._get_last_application(user_id)
        application_id = application.id
        message = await application_format.format_application(application_id, session)
        await session.commit()
    await bot.send_message(
        text=message,
        chat_id=admin_chat,
        reply_markup=keyboards.ADMIN_DECISION_KEYBOARD(application_id),
        parse_mode="MarkdownV2",
    )
