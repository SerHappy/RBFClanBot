from db import Database
from db import Session
from decouple import config
from loguru import logger
from services import formatting_service
from telegram import Bot
from datetime import timedelta
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
        message = await formatting_service.format_application(application_id, session)
        await session.commit()
    await bot.send_message(
        text=message,
        chat_id=admin_chat,
        reply_markup=keyboards.ADMIN_DECISION_KEYBOARD(application_id),
        parse_mode="MarkdownV2",
    )


async def send_admin_decision_to_user(application_id: int, bot: Bot) -> None:
    """
    Обработка решения админа.

    Args:
        application_id: ID заявки.
        bot: Телеграм бот.

    Returns:
        None
    """
    logger.info(f"Обработка решения админа application_id={application_id}")
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        application = await db.application.get(application_id)
        application_status = application.status_id
        if application_status == 3:
            logger.debug(f"Заявка application_id={application_id} принята, уведомляем пользователя и отправляем инвайт")
            await bot.send_message(
                chat_id=application.user_id,
                text="Ваша заявка принята!\nВаша персональная ссылка: {}".format(application.invite_link),
            )
        elif application_status == 4:
            logger.debug(
                f"Заявка application_id={application_id} отклонена, уведомляем пользователя и отправляем причину отказа"
            )
            await bot.send_message(
                chat_id=application.user_id,
                text="Ваша заявка отклонена.\nПричина отказа: {}.\nПопробуйте снова {} (UTC+0).".format(
                    application.rejection_reason,
                    (timedelta(days=30) + application.decision_date).strftime("%d.%m.%Y %H:%M"),
                ),
            )
        await bot.send_message(
            chat_id=application.user_id,
            text="Если у вас есть какие-то вопросы или предложения по улучшению, напишите @RBFManager",
        )
        await session.commit()
