from config import DeclineUserStates
from db import Database
from db import Session
from decorators import updates
from loguru import logger
from services import formatting_service
from services import message_service
from telegram import CallbackQuery
from telegram import Chat
from telegram import Message
from telegram.ext import CallbackContext
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

import keyboards


@updates.check_update_and_provide_data(need_callback=True)
async def reject_application_start(callback: CallbackQuery, chat: Chat, context: CallbackContext) -> int:
    """
    Обработчик коллбека отклонения заявки.

    Args:
        update: Объект Update.
        context: Объект CallbackContext.

    Returns:
        Следующее состояние или ConversationHandler.END
    """
    if not callback.data:
        logger.error("Получен некорректный callback при попытке вызова accept_application.")
        return ConversationHandler.END
    context.user_data["message"] = callback.message  # type: ignore
    logger.debug(f"Сохранение переменной message={callback.message}.")
    application_id = int(callback.data.split(":")[-1])
    logger.info(f"Отклонение заявки application_id={application_id}.")
    context.user_data["application_id"] = application_id  # type: ignore
    logger.debug(f"Сохранение переменной application_id={application_id}.")
    await callback.edit_message_reply_markup(keyboards.ADMIN_DECLINE_BACK_KEYBOARD)
    logger.debug("Клавиатура обновлена.")
    await chat.send_message("Напишите причину отказа для Заявки №{}".format(application_id))
    return DeclineUserStates.decline_reason_state


@updates.check_update_and_provide_data(need_message=True)
async def reject_reason_hander(message: Message, chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик причины отказа.

    Args:
        update: Объект Update.
        context: Объект CallbackContext.

    Returns:
        ConversationHandler.END

    """
    if not message.text:
        logger.error("Получена некорректная причина отказа.")
        return ConversationHandler.END
    application_id = context.user_data["application_id"]  # type: ignore
    logger.info(f"Получение причины отказа application_id={application_id}.")
    await chat.send_message(
        "Причина отказа для Заявки №{}:\n{}.".format(application_id, message.text),
    )
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db: Database = Database(session)
        await db.application.reject_application(application_id, message.text)
        new_text = await formatting_service.format_application(application_id, session)
        await session.commit()
    bot = context.application.bot
    message: Message = context.user_data["message"]  # type: ignore
    await message.edit_text(text=new_text, reply_markup=keyboards.REMOVE_INLINE_KEYBOARD, parse_mode="MarkdownV2")
    logger.debug("Текст заявки обновлен.")
    await chat.send_message("Заявка №{} отклонена.".format(application_id))
    await message_service.send_admin_decision_to_user(application_id, bot)
    return ConversationHandler.END


@updates.check_update_and_provide_data(need_callback=True)
async def reject_back_button_handler(callback: CallbackQuery, chat: Chat, context: CallbackContext) -> int:
    """
    Обработчик кнопки Назад в чате админов.

    Args:
        update: Объект Update.
        context: Объект CallbackContext.

    Returns:
        ConversationHandler.END
    """
    logger.debug("In decline back handler.")
    logger.info("Возврат к выбору действий для Заявки.")
    application_id = context.user_data["application_id"]  # type: ignore
    logger.debug("Возврат к выбору действий для Заявки №{}".format(application_id))
    await callback.edit_message_reply_markup(keyboards.ADMIN_DECISION_KEYBOARD(application_id))
    return ConversationHandler.END
