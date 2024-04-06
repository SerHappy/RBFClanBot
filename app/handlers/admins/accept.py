from db import Database
from db import Session
from decorators import updates
from loguru import logger
from services import formatting_service
from services import link_service
from services import message_service
from telegram import CallbackQuery
from telegram import Chat
from telegram.ext import CallbackContext

import keyboards


@updates.check_update_and_provide_data(need_callback=True)
async def accept_application(callback: CallbackQuery, chat: Chat, context: CallbackContext) -> None:
    """
    Обработчик коллбека принятия заявки.

    Args:
        update: Объект Update.
        context: Объект CallbackContext.

    Returns:
        None
    """
    if not callback.data:
        logger.error("Получен некорректный callback при попытке вызова accept_application.")
        return
    application_id = int(callback.data.split(":")[-1])
    logger.info(f"Принятие заявки application_id={application_id}.")
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db: Database = Database(session)
        link = await link_service.generate_invite_link(context.application.bot)
        await db.application.approve_application(application_id, link)
        new_text = await formatting_service.format_application(application_id, session)
        await session.commit()
    await callback.edit_message_reply_markup(keyboards.REMOVE_INLINE_KEYBOARD)
    await callback.edit_message_text(new_text, parse_mode="MarkdownV2")
    logger.debug("Текст заявки обновлен.")
    await chat.send_message("Заявка №{} принята.".format(application_id))
    bot = context.application.bot
    await message_service.send_admin_decision_to_user(application_id, bot)
