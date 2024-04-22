import keyboards
from db import Database, session_factory
from decorators import updates
from loguru import logger
from services import formatting_service
from telegram import CallbackQuery, Chat
from telegram.ext import ContextTypes, ConversationHandler


# TODO: Переименовать функцию
@updates.check_update_and_provide_data(need_callback=True)
async def take_application_handler(
    callback: CallbackQuery, chat: Chat, context: ContextTypes.DEFAULT_TYPE
):
    """
    Взятие заявки в обработку.

    Args:
        call: CallbackQuery.
        callback_data: Данные коллбека.

    Returns:
        None
    """
    callback_data = callback.data
    admin_id = callback.from_user.id
    application_message = callback.message
    if not callback_data or not application_message:
        logger.error(
            "Получен некорректный callback или message при попытке вызова take_application."
        )
        return ConversationHandler.END
    application_id = int(callback_data.split(":")[-1])
    logger.info(f"Администратор {admin_id=} взял заявку {application_id=} в обработку.")
    async with session_factory() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        application = await db.application.get(application_id)
        admin_processing_application = (
            await db.admin_processing_application.get_admin_processing_application(
                admin_id
            )
        )
        if application.status_id != 2:
            logger.error(
                f"Попытка взять в обработку заявку {application_id=} с неверным статусом {application.status_id=} "
            )
            await callback.answer(
                text=f"Невозможно взять в обработку заявку со статусом {application.status_id=}",
                show_alert=True,
            )
            return ConversationHandler.END
        if admin_processing_application:
            print(admin_processing_application)
            logger.error(
                f"Попытка взять в обработку заявку {application_id=} админом {admin_id=}, который уже обрабатывает заявку"
            )
            await callback.answer(
                text=f"Вы уже взяли заявку {admin_processing_application.application_id} в обработку. Обработайте ее прежде чем взять еще одну",
                show_alert=True,
            )
            return ConversationHandler.END
        await db.application.change_status(application_id, 5)
        await db.admin_processing_application.create(admin_id, application_id)
        await session.commit()
        await application_message.edit_text(
            text=await formatting_service.format_application(application_id, session),
            reply_markup=None,
            parse_mode="MarkdownV2",
        )
        await context.application.bot.send_message(
            chat_id=admin_id,
            text=await formatting_service.format_application(application_id, session),
            reply_markup=keyboards.ADMIN_DECISION_KEYBOARD(application_id),
            parse_mode="MarkdownV2",
        )
    context.user_data["application_message_id"] = application_message.message_id  # type: ignore
    await callback.answer(
        text="Заявка взята в обработку! Зайдите в личные сообщения для дальнейшей работы.",
        show_alert=True,
    )
