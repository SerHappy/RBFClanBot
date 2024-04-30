import keyboards
from loguru import logger
from telegram import Chat, Message, User, constants
from telegram.ext import ContextTypes, ConversationHandler

from app.config import ApplicationStates
from app.db import UnitOfWork
from app.decorators import updates
from app.domain.application.exceptions import (
    ApplicationAlreadyAcceptedError,
    ApplicationAtWaitingStatusError,
    ApplicationCoolDownError,
    ApplicationDecisionDateNotFoundError,
    ApplicationWrongStatusError,
)
from app.domain.user.exceptions import (
    UserIsBannedError,
)
from app.services.applications.application_start import ApplicationStartService
from app.services.users.dto import UserCreateDTO
from app.services.users.user_create import EnsureUserExistsService


@updates.check_application_update(
    return_error_state=ConversationHandler.END,
    return_full_user=True,
)
async def start_command(  # noqa: PLR0911
    user: User,
    chat: Chat,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
    message: Message | None = None,  # noqa: ARG001
) -> int | None:
    """
    Входная точка для заполнения анкеты.

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
        ApplicationDecisionDateNotFoundError,
        ApplicationWrongStatusError,
    ):
        await chat.send_message(
            "Что-то не так...\n"
            "Свяжитесь с менеджером @RBFManager для решения этой проблемы.",
        )
        return ConversationHandler.END
    except UserIsBannedError:
        await chat.send_message(
            "Вы были заблокированы. Заполнение анкеты невозможно.",
        )
        return ConversationHandler.END
    except ApplicationAlreadyAcceptedError:
        await chat.send_message("Ваша заявка уже была принята")
        return ConversationHandler.END
    except ApplicationAtWaitingStatusError:
        await chat.send_message("Ваша заявка на рассмотрении")
        return ConversationHandler.END
    except ApplicationCoolDownError as e:
        await chat.send_message(
            (
                "Подача повторной заявки возможна только раз в месяц.\n"
                "Вы сможете подать заявку "
                f"{e.cooldown_ends.strftime('%d.%m.%Y %H:%M %Z')}"
            ),
        )
        return ConversationHandler.END

    logger.info(
        (
            f"Пользователь chat_id={chat.id} начинает заполнять анкету"
            f"переводим в состояние {ApplicationStates.PUBG_ID_STATE}"
        ),
    )
    await _send_greeting(chat)
    await _ask_for_pubg_id(chat)
    return ApplicationStates.PUBG_ID_STATE.value


async def _send_greeting(chat: Chat) -> None:
    """
    Отправить приветственное сообщение в чат.

    Args:
    ----
        chat: Чат.

    Returns:
    -------
        None.

    """
    logger.debug(f"Отправляем приветственное сообщения в чат chat_id={chat.id}.")
    await chat.send_message(
        (
            "Приветствую!\n"
            "Для вступления в клан надо заполнить заявку."
            "Будь готов ответить на 5 вопросов!\n"
        ),
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )


async def _ask_for_pubg_id(chat: Chat) -> None:
    """
    Запросить ответ на pubg_id.

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
