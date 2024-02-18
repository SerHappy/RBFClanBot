from config import ApplicationStates
from db import Database
from db import Session
from loguru import logger
from telegram import Chat
from telegram import InlineKeyboardMarkup
from telegram import Message
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram import User
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

import keyboards


async def pubg_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Pubg ID handler."""
    logger.debug("Starting handle pubg_id answer")
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.critical("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    return await _process_application_answer(
        user=user,
        chat=chat,
        message=message,
        question_number=1,
        next_message="Сколько тебе полных лет?",
        keyboard=keyboards.REMOVE_KEYBOARD,
        next_state=ApplicationStates.old_state,
    )


async def old(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Old handler."""
    logger.debug("Starting handle old answer")
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.critical("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    return await _process_application_answer(
        user=user,
        chat=chat,
        message=message,
        question_number=2,
        next_message="Какие режимы игры предпочитаешь больше всего? (можно несколько)",
        keyboard=keyboards.REMOVE_KEYBOARD,
        next_state=ApplicationStates.game_modes_state,
    )


async def game_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Game mode handler."""
    logger.debug("Starting handle game_mode answer")
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.critical("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    return await _process_application_answer(
        user=user,
        chat=chat,
        message=message,
        question_number=3,
        next_message="Сколько времени в день готов уделять игре с соклановцами? (примерно; можно по дням)",
        keyboard=keyboards.REMOVE_KEYBOARD,
        next_state=ApplicationStates.activity_state,
    )


async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Activity handler."""
    logger.debug("Starting handle activity answer")
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.critical("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    return await _process_application_answer(
        user=user,
        chat=chat,
        message=message,
        question_number=4,
        next_message="Расскажи о себе, либо пропусти вопрос.\n"
        + "Чем больше информации мы о тебе получим, тем выше вероятность одобрения заявки.",
        keyboard=keyboards.USER_SKIP_KEYBOARD,
        next_state=ApplicationStates.about_state,
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """About handler."""
    logger.debug("Starting handle about answer")
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.critical("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    answer = message.text
    if answer == "Пропустить":
        answer = "Пусто"
    if await _is_new_answer(user, 5) is False:
        await _update_answer(user, 5, answer)
    else:
        await _save_answer(user, 5, answer)
    return await _show_overview(chat)


async def _show_overview(chat) -> ApplicationStates.change_or_accept_state:
    logger.debug(f"Showing overview for chat={chat.id}")
    async with Session() as session:
        db = Database(session)
        application = await db.application.get_last_application(user_id=chat.id)
        answers = await db.application_answer.get_all_answers_by_application_id(application.id)
        print(answers)
    await chat.send_message(
        f"Твоя заявка:\n\n1. PUBG ID: {answers[0].answer_text}\n2. Возраст: {answers[1].answer_text}\n3. Режимы игры: {answers[2].answer_text}\n4. Активность: {answers[3].answer_text}\n5. О себе: {answers[4].answer_text}\nВсе верно?",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )
    await chat.send_message(
        "1. Изменить PubgID\n2. Изменить возраст\n3. Изменить режимы игры\n4. Изменить частоту активности\n5. Изменить 'о себе'\n6. Все верно!",
        reply_markup=keyboards.USER_DECISION_KEYBOARD,
    )
    return ApplicationStates.change_or_accept_state


async def user_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """1-6 answer for application. If 1-5 - ask this question again, if 6 - accept application."""
    logger.debug("Starting handle user_decision answer")
    user = update.effective_user
    chat = update.effective_chat
    if user is None or chat is None or update.message is None or context.user_data is None:
        logger.critical("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    logger.debug(f"User {user} answer for change_or_accept: {update.message.text}")
    answer = update.message.text
    return await _choose_action(answer, user, chat, context)


async def _choose_action(answer: str | None, user: User, chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug(f"Choosing action for user {user} answer: {answer}")
    if answer == "1":
        await _ask_next_question(
            chat,
            "Напиши свой PUBG ID",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.pubgID_state
    if answer == "2":
        await _ask_next_question(
            chat,
            "Напиши свой возраст",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.old_state
    if answer == "3":
        await _ask_next_question(
            chat,
            "Какие режимы игры предпочитаешь больше всего? (можно несколько)",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.game_modes_state
    if answer == "4":
        await _ask_next_question(
            chat,
            "Сколько времени в день готов уделять игре с соклановцами?",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.activity_state
    if answer == "5":
        await _ask_next_question(
            chat,
            "Расскажи о себе либо пропусти вопрос. Чем больше информации мы о тебе получим, тем выше вероятность одобрения заявки.",
            keyboards.USER_SKIP_KEYBOARD,
        )
        return ApplicationStates.about_state
    if answer == "6":
        await _change_application_status_to_waiting(user)
        await chat.send_message(
            "Заявка принята!",
            reply_markup=keyboards.REMOVE_KEYBOARD,
        )
        return ConversationHandler.END
    await chat.send_message("Неверная команда")
    return ApplicationStates.change_or_accept_state


async def _process_application_answer(
    user: User,
    chat: Chat,
    message: Message,
    question_number: int,
    next_message: str,
    keyboard: ReplyKeyboardMarkup | ReplyKeyboardRemove | InlineKeyboardMarkup,
    next_state: ApplicationStates,
) -> int:
    """
    Process application answer.

    Args:
        user: User.
        chat: Chat.
        message: Message.
        question_number: Question number.
        next_message: Next message.
        keyboard: Keyboard.
        next_state: Next state.

    Returns:
        Next state.
    """
    logger.debug(f"User {user} answer for question {question_number}: {message.text}")
    if await _is_new_answer(user, question_number) is False:
        await _update_answer(user, question_number, message.text)
        return await _show_overview(chat)
    await _save_answer(user, question_number, message.text)
    await _ask_next_question(chat, next_message, keyboard)
    return next_state


async def _change_application_status_to_waiting(user: User):
    logger.debug(f"Changing application status to waiting for user {user}")
    async with Session() as session:
        db = Database(session)
        user_application = await db.application.get_last_application(user.id)
        logger.debug(f"User {user} last application: {user_application}")
        await db.application.change_status(user_application.id, 2)
        await session.commit()


async def _is_new_answer(user, question_number) -> bool:
    logger.debug(f"Checking if user {user} has new answer for question {question_number}")
    async with Session() as session:
        db = Database(session)
        user_application = await db.application.get_last_application(user.id)
        logger.debug(f"User {user} last application: {user_application}")
        user_answer = await db.application_answer.get_answer_by_question_number(user_application.id, question_number)
        logger.debug(f"User {user} answer for question ({question_number}): {user_answer}")
        return user_answer is None


async def _save_answer(user, question_number, answer) -> None:
    logger.debug(f"Saving answer for user {user} for question {question_number} with answer {answer}")
    async with Session() as session:
        db = Database(session)
        user_application = await db.application.get_last_application(user.id)
        logger.debug(f"User {user} last application: {user_application}")
        logger.debug(f"User {user} answer for question {question_number} added to {answer}")
        await db.application_answer.create(user_application.id, question_number, answer)
        await session.commit()


async def _update_answer(user, question_number, answer) -> None:
    logger.debug(f"Updating answer for user {user} for question {question_number} with answer {answer}")
    async with Session() as session:
        db = Database(session)
        user_application = await db.application.get_last_application(user.id)
        logger.debug(f"User {user} last application: {user_application}")
        logger.debug(f"User {user} answer for question {question_number} updated to {answer}")
        await db.application_answer.update_question_answer(user_application.id, question_number, answer)
        await session.commit()


async def _ask_next_question(chat, next_message, keyboard) -> None:
    logger.debug(f"Asking next question: {next_message}")
    await chat.send_message(
        text=next_message,
        reply_markup=keyboard,
    )
