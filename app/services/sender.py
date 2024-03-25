from db import Database
from db import Session
from decouple import config
from loguru import logger
from telegram import Bot
from utils import application_format

import keyboards


async def send_application_to_admins(bot: Bot, user_id: int) -> None:
    """
    Отправка заявки админам.

    Args:
        bot: Телеграм бот.
        user_id: ID пользователя.

    Returns:
        None
    """
    admin_chat = config("ADMIN_CHAT_ID", cast=int)
    logger.info(f"Отправка заявки пользователя user_id={user_id} админам в чат admin_chat_id={admin_chat}.")
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        application = await db.application.get_active_application(user_id)
        application_id = application.id
        message = await application_format.format_application(application_id, session)
        await session.commit()
    await bot.send_message(
        text=message,
        chat_id=admin_chat,
        reply_markup=keyboards.ADMIN_DECISION_KEYBOARD(application_id),
        parse_mode="MarkdownV2",
    )
