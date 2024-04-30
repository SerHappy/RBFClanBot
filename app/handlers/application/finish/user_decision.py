from loguru import logger
from telegram import Chat, Message
from telegram.ext import ContextTypes, ConversationHandler, ExtBot

from app import keyboards
from app.core.config import settings
from app.db.engine import UnitOfWork
from app.decorators import updates
from app.handlers.config.states import ApplicationStates
from app.services.applications.application_complete import (
    ApplicationCompleteService,
)
from app.services.applications.application_formatting import (
    ApplicationFormattingService,
)


@updates.check_application_update()
async def user_decision(
    user_id: int,
    chat: Chat,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Respond to user decision."""
    logger.info(f"Обработка варианта ответа пользователя для chat_id={chat.id}")
    return await _handle_answer_change_request(user_id, message.text, context.bot)


async def _handle_answer_change_request(
    user_id: int,
    decision: str | None,
    bot: ExtBot,
) -> int:
    messages = {
        "1": (
            "Напиши свой PUBG ID",
            ApplicationStates.PUBG_ID_STATE,
            keyboards.REMOVE_KEYBOARD,
        ),
        "2": (
            "Сколько тебе полных лет?",
            ApplicationStates.AGE_STATE,
            keyboards.REMOVE_KEYBOARD,
        ),
        "3": (
            "Какие режимы игры предпочитаешь больше всего? (можно несколько)",
            ApplicationStates.GAME_MODES_STATE,
            keyboards.REMOVE_KEYBOARD,
        ),
        "4": (
            (
                "Сколько времени в день готов уделять игре с соклановцами? "
                "(примерно; можно по дням)"
            ),
            ApplicationStates.ACTIVITY_STATE,
            keyboards.REMOVE_KEYBOARD,
        ),
        "5": (
            (
                "Расскажи о себе либо пропусти вопрос. "
                "Чем больше информации мы о тебе получим, "
                "тем выше вероятность одобрения заявки."
            ),
            ApplicationStates.ABOUT_STATE,
            keyboards.USER_SKIP_KEYBOARD,
        ),
    }
    if decision in messages:
        message, state, keyboard = messages[decision]
        await bot.send_message(user_id, message, reply_markup=keyboard)
        return state.value
    return await _handle_application_complete(user_id, decision, bot)


async def _handle_application_complete(
    user_id: int,
    decision: str | None,
    bot: ExtBot,
) -> int:
    if decision == "6":
        uow = UnitOfWork()
        application_complete_service = ApplicationCompleteService(uow)
        application = await application_complete_service.execute(user_id)
        formatting_service = ApplicationFormattingService(uow)
        formatted_application = await formatting_service.execute(application.id)
        await bot.send_message(
            text=formatted_application,
            chat_id=settings.ADMIN_CHAT_ID,
            reply_markup=keyboards.ADMIN_HANDLE_APPLICATION_KEYBOARD(application.id),
            parse_mode="MarkdownV2",
        )
        await bot.send_message(
            user_id,
            "Заявка отправлена, ожидай ответа!",
            reply_markup=keyboards.REMOVE_KEYBOARD,
        )
        return ConversationHandler.END
    await bot.send_message(user_id, "Неверная команда. Выбери число от 1 до 6.")
    return ApplicationStates.CHANGE_OR_ACCEPT_STATE.value
