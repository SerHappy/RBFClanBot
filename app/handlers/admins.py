from config import DeclineUserStates
from db import Database
from db import Session
from decouple import config
from handlers.application import handle_admin_decision
from loguru import logger
from telegram import Bot
from telegram import ChatInviteLink
from telegram import Message
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from utils import application_format

import keyboards


async def accept_user(update: Update, context: CallbackContext) -> None:
    """
    Обработчик коллбека принятия заявки.

    Args:
        update: Объект Update.
        context: Объект CallbackContext.

    Returns:
        None
    """
    callback = update.callback_query
    chat = update.effective_chat

    if chat is None or callback is None or callback.data is None:
        logger.critical(
            "Чат или коллбек не определены при получении коллбека accept_user! Данная ошибка не должна никогда происходить."
        )
        return

    application_id = int(callback.data.split(":")[-1])
    logger.info(f"Принятие заявки application_id={application_id}.")
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db: Database = Database(session)
        link = await _generate_invite_link(context.application.bot)
        await db.application.approve_application(application_id, link)
        new_text = await application_format.format_application(application_id, session)
        await session.commit()
    await callback.edit_message_reply_markup(keyboards.REMOVE_INLINE_KEYBOARD)
    await callback.edit_message_text(new_text, parse_mode="MarkdownV2")
    logger.debug("Текст заявки обновлен.")
    await chat.send_message("Заявка №{} принята.".format(application_id))
    bot = context.application.bot
    await handle_admin_decision(application_id, bot)


async def decline_user(update: Update, context: CallbackContext) -> int:
    """
    Обработчик коллбека отклонения заявки.

    Args:
        update: Объект Update.
        context: Объект CallbackContext.

    Returns:
        Следующее состояние или ConversationHandler.END
    """
    callback = update.callback_query
    chat = update.effective_chat

    if chat is None or callback is None or callback.data is None:
        logger.critical(
            "Чат или коллбек не определены при получении коллбека accept_user! Данная ошибка не должна никогда происходить."
        )
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


async def decline_reason_hander(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик причины отказа.

    Args:
        update: Объект Update.
        context: Объект CallbackContext.

    Returns:
        ConversationHandler.END

    """
    application_id = context.user_data["application_id"]  # type: ignore
    chat = update.effective_chat
    rejection_reason = update.message
    if chat is None or rejection_reason is None:
        logger.critical(
            "Чат или причина отказа не определены в обработчике decline_reason_hander! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END

    logger.info(f"Получение причины отказа application_id={application_id}.")
    await chat.send_message(
        "Причина отказа для Заявки №{}:\n{}.".format(application_id, rejection_reason.text),
    )
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db: Database = Database(session)
        await db.application.reject_application(application_id, rejection_reason.text)
        new_text = await application_format.format_application(application_id, session)
        await session.commit()
    bot = context.application.bot
    message: Message = context.user_data["message"]  # type: ignore
    await message.edit_text(text=new_text, reply_markup=keyboards.REMOVE_INLINE_KEYBOARD, parse_mode="MarkdownV2")
    logger.debug("Текст заявки обновлен.")
    await chat.send_message("Заявка №{} отклонена.".format(application_id))
    await handle_admin_decision(application_id, bot)
    return ConversationHandler.END


async def decline_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик кнопки Назад в чате админов.

    Args:
        update: Объект Update.
        context: Объект CallbackContext.

    Returns:
        ConversationHandler.END
    """
    logger.debug("In decline back handler.")
    callback = update.callback_query
    chat = update.effective_chat

    if callback is None or callback.data is None or chat is None:
        logger.critical(
            "Чат или коллбек отказа не определены в обработчике decline_back_handler! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END
    logger.info("Возврат к выбору действий для Заявки.")
    application_id = context.user_data["application_id"]  # type: ignore
    logger.debug("Возврат к выбору действий для Заявки №{}".format(application_id))
    await callback.edit_message_reply_markup(keyboards.ADMIN_DECISION_KEYBOARD(application_id))
    return ConversationHandler.END


async def _generate_invite_link(bot: Bot) -> str:
    """
    Генерирует и возвращает ссылку на приглашение.

    Args:
        bot: Объект Bot.

    Returns:
        Ссылка на приглашение.
    """
    logger.debug("In generate invite link handler.")
    chat_id = config("ADMIN_CHAT_ID", cast=int)
    link: ChatInviteLink = await bot.create_chat_invite_link(chat_id, member_limit=1)
    return "Тут будет ссылка"
    # return link.invite_link
