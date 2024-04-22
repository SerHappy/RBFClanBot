from core.config import settings
from db import Database, Session
from decorators import updates
from loguru import logger
from services import formatting_service, link_service, message_service
from telegram import CallbackQuery, Chat
from telegram.ext import ContextTypes


@updates.check_update_and_provide_data(need_callback=True)
async def accept_application(
    callback: CallbackQuery, chat: Chat, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Обработчик коллбека принятия заявки.

    Args:
        update: Объект Update.
        context: Объект CallbackContext.

    Returns:
        None
    """
    if not callback.data:
        logger.error(
            "Получен некорректный callback при попытке вызова accept_application."
        )
        return
    application_id = int(callback.data.split(":")[-1])
    logger.info(f"Принятие заявки application_id={application_id}.")
    admin_id = callback.from_user.id
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db: Database = Database(session)
        link = await link_service.generate_invite_link(context.application.bot)
        await db.application.approve_application(application_id, link)
        await db.admin_processing_application.delete(admin_id)
        new_text = await formatting_service.format_application(application_id, session)
        await session.commit()
    await callback.edit_message_text(new_text, parse_mode="MarkdownV2")
    bot = context.application.bot
    await message_service.send_admin_decision_to_user(application_id, bot)
    await context.application.bot.edit_message_text(
        new_text,
        chat_id=settings.ADMIN_CHAT_ID,
        message_id=context.user_data["application_message_id"],  # type: ignore
        parse_mode="MarkdownV2",
    )
    logger.debug("Текст заявки обновлен.")
    await chat.send_message("Заявка №{} принята.".format(application_id))
