from . import preprocessing_checks
from config import ApplicationStates
from db import Database
from db import Session
from decorators import updates
from loguru import logger
from telegram import Chat
from telegram import constants
from telegram import Message
from telegram import User
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

import keyboards


@updates.check_application_update(return_error_state=ConversationHandler.END, return_full_user=True)
async def start_command(
    user: User,
    chat: Chat,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> ApplicationStates.pubgID_state:
    """
    Входная точка для заполнения анкеты.

    Вызывается при вызове команды /start.

    Args:
        update: Объект Update.
        context: Объект ContextTypes.DEFAULT_TYPE.

    Returns:
        Переводит в состояние ApplicationStates.pubgID_state.
    """
    # TODO: Вынести в декоратор
    chat_type = chat.type
    if chat_type != constants.ChatType.PRIVATE:
        await chat.send_message("Эту команду можно вызывать только в личной беседе с ботом.")
        return ConversationHandler.END

    logger.info(f"Пользователь чата chat_id={chat.id} вызвал команду /start")
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        user_repo = db.user
        application_repo = db.application

        db_user = await user_repo.create_if_not_exists(user.id, user.username, user.first_name, user.last_name)
        # TODO: Сохранять только статус
        await application_repo.create_if_not_exists(db_user.id)

        result = await preprocessing_checks.check_user_ability_to_fill_application(user.id, chat, session)

        await session.commit()

    if result is False:
        logger.info(f"Пользователь chat_id={chat.id} не может заполнять анкету , выход из /start")
        return ConversationHandler.END
    context.user_data["application_completed"] = False  # type: ignore
    logger.debug("Создана переменная application_completed, значение которой равно False")
    logger.info(
        f"Пользователь chat_id={chat.id} начинает заполнять анкету, переводим в состояние {ApplicationStates.pubgID_state}"
    )
    await _send_greeting(chat)
    return await _ask_for_pubg_id(chat)


async def _send_greeting(chat: Chat) -> None:
    """
    Отправить приветственное сообщение в чат.

    Args:
        chat: Чат.

    Returns:
        None.
    """
    logger.debug(f"Отправляем приветственное сообщения в чат chat_id={chat.id}.")
    await chat.send_message(
        "Приветствую!\nДля вступления в клан надо заполнить заявку. Будь готов ответить на 5 вопросов!\n",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )


async def _ask_for_pubg_id(chat: Chat) -> ApplicationStates.pubgID_state:
    """
    Запросить ответ на pubg_id.

    Args:
        chat: Чат.

    Returns:
        Новое состояние ApplicationStates.pubgID_state.
    """
    logger.debug(f"Запрашиваем ответ на pubg_id в чате chat_id={chat.id}.")
    await chat.send_message(
        "Напиши свой pubgID",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )
    return ApplicationStates.pubgID_state
