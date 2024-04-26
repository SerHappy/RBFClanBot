import keyboards
from config import ApplicationStates
from db import UnitOfWork
from decorators import updates
from loguru import logger
from telegram import Chat, Message, User, constants
from telegram.ext import ContextTypes, ConversationHandler

from app.domain.application.exceptions import (
    ApplicationAlreadyAcceptedError,
    ApplicationAtWaitingStatusError,
    ApplicationDecisionDateNotFoundError,
    ApplicationWrongStatusError,
)
from app.domain.user.exceptions import (
    UserAlreadyExistsError,
    UserIsBannedError,
    UserNotFoundError,
)
from app.services.applications.application_start import ApplicationStartService
from app.services.users.dto import UserCreateDTO
from app.services.users.user_create import EnsureUserExistsService


@updates.check_application_update(
    return_error_state=ConversationHandler.END,
    return_full_user=True,
)
async def start_command(
    user: User,
    chat: Chat,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int | None:
    """Входная точка для заполнения анкеты.

    Вызывается при вызове команды /start.
    """
    chat_type = chat.type
    if chat_type != constants.ChatType.PRIVATE:
        await chat.send_message(
            "Эту команду можно вызывать только в личной беседе с ботом.",
        )
        return ConversationHandler.END

    logger.info(f"Пользователь чата chat_id={chat.id} вызвал команду /start")

    uow = UnitOfWork()
    user_service = EnsureUserExistsService(uow)
    application_service = ApplicationStartService(uow)
    try:
        user_create_dto = UserCreateDTO(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        user_entity = await user_service.execute(data=user_create_dto)
        await application_service.execute(user_entity.id)
    except (
        UserAlreadyExistsError,
        UserIsBannedError,
        UserNotFoundError,
        ApplicationAlreadyAcceptedError,
        ApplicationAtWaitingStatusError,
        ApplicationDecisionDateNotFoundError,
        ApplicationWrongStatusError,
    ):
        return ConversationHandler.END

    context.user_data["application_completed"] = False  # type: ignore[reportOptionalSubscript]
    logger.info(
        (
            f"Пользователь chat_id={chat.id} начинает заполнять анкету"
            f"переводим в состояние {ApplicationStates.pubgID_state}"
        ),
    )
    await _send_greeting(chat)
    return await _ask_for_pubg_id(chat)


async def _send_greeting(chat: Chat) -> None:
    """Отправить приветственное сообщение в чат.

    Args:
    ----
        chat: Чат.

    Returns:
    -------
        None.

    """
    logger.debug(f"Отправляем приветственное сообщения в чат chat_id={chat.id}.")
    await chat.send_message(
        "Приветствую!\nДля вступления в клан надо заполнить заявку. Будь готов ответить на 5 вопросов!\n",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )


async def _ask_for_pubg_id(chat: Chat) -> ApplicationStates.pubgID_state:
    """Запросить ответ на pubg_id.

    Args:
    ----
        chat: Чат.

    Returns:
    -------
        Новое состояние ApplicationStates.pubgID_state.

    """
    logger.debug(f"Запрашиваем ответ на pubg_id в чате chat_id={chat.id}.")
    await chat.send_message(
        "Напиши свой PUBG ID",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )
    return ApplicationStates.pubgID_state
