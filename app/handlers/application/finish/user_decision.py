import keyboards
from config import ApplicationStates
from decorators import updates
from loguru import logger
from services import application, message_service
from telegram import Chat, Message
from telegram.ext import ContextTypes, ConversationHandler


@updates.check_application_update()
async def user_decision(
    user_id: int,
    chat: Chat,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """
    Обработка ввода варианта ответа при изменении или принятия заявки.

    Если ответ 1-5 - переход на соответствующее состояние и изменение ответа в базе данных.
    Если ответ 6 - отправка заявки администраторам и перевод в состояние ConversationHandler.END.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Состояние для изменения или ConversationHandler.END.
    """
    logger.info(f"Обработка варианта ответа пользователя для chat_id={chat.id}")

    context.user_data["application_completed"] = True  # type: ignore
    logger.debug(f"Переменная application_completed для chat_id={chat.id} установлена в True")

    logger.info(f"Пользователь chat_id={chat.id} ответил на вопрос overview: {message.text}")

    return await _choose_action(message.text, user_id, chat, context)


async def _choose_action(answer: str | None, user_id: int, chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Выбор действия для пользователя.

    Args:
        answer: Ответ пользователя.
        user: Пользователь.
        chat: Чат.
        context: Контекст.

    Returns:
        Состояние для изменения или ConversationHandler.END.

    """
    logger.debug(f"Выбор действия для пользователя user={user_id}")
    if answer == "1":
        logger.debug(f"Пользователь user={user_id} выбрал изменить PubgID")
        await application.ask_next_question(
            chat,
            "Напиши свой PUBG ID",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.pubgID_state
    if answer == "2":
        logger.debug(f"Пользователь user={user_id} выбрал изменить возраст")
        await application.ask_next_question(
            chat,
            "Сколько тебе полных лет?",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.age_state
    if answer == "3":
        logger.debug(f"Пользователь user={user_id} выбрал изменить режимы игры")
        await application.ask_next_question(
            chat,
            "Какие режимы игры предпочитаешь больше всего? (можно несколько)",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.game_modes_state
    if answer == "4":
        logger.debug(f"Пользователь user={user_id} выбрал изменить частоту активности")
        await application.ask_next_question(
            chat,
            "Сколько времени в день готов уделять игре с соклановцами? (примерно; можно по дням)",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.activity_state
    if answer == "5":
        logger.debug(f"Пользователь user={user_id} выбрал изменить о себе")
        await application.ask_next_question(
            chat,
            "Расскажи о себе либо пропусти вопрос. Чем больше информации мы о тебе получим, тем выше вероятность одобрения заявки.",
            keyboards.USER_SKIP_KEYBOARD,
        )
        return ApplicationStates.about_state
    if answer == "6":
        logger.debug(f"Пользователь user={user_id} выбрал отправить заявку администраторам")
        await application.change_application_status_to_waiting(user_id)
        await chat.send_message(
            "Заявка отправлена, ожидай ответа!",
            reply_markup=keyboards.REMOVE_KEYBOARD,
        )
        await message_service.send_application_to_admins(bot=context.bot, user_id=user_id)
        return ConversationHandler.END
    logger.debug(f"Пользователь user={user_id} ввел неверную команду")
    await chat.send_message("Неверная команда. Выбери число от 1 до 6.")
    return ApplicationStates.change_or_accept_state
