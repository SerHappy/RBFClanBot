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


async def _is_new_answer(user, question_number) -> bool:
    async with Session() as session:
        db = Database(session)
        user_application = await db.application.get_last_application(user.id)
        logger.debug(f"User {user} last application: {user_application}")
        user_answer = await db.application_answer.get_answer_by_question_number(user_application.id, question_number)
        logger.debug(f"User {user} answer for question ({question_number}): {user_answer}")
        return user_answer is None


async def _save_answer(user, question_number, answer) -> None:
    async with Session() as session:
        db = Database(session)
        user_application = await db.application.get_last_application(user.id)
        logger.debug(f"User {user} last application: {user_application}")
        logger.debug(f"User {user} answer for question {question_number} added to {answer}")
        await db.application_answer.create(user_application.id, question_number, answer)
        await session.commit()


async def _update_answer(user, question_number, answer) -> None:
    async with Session() as session:
        db = Database(session)
        user_application = await db.application.get_last_application(user.id)
        logger.debug(f"User {user} last application: {user_application}")
        logger.debug(f"User {user} answer for question {question_number} updated to {answer}")
        await db.application_answer.update_question_answer(user_application.id, question_number, answer)
        await session.commit()


async def _ask_next_question(chat, next_message, keyboard) -> None:
    await chat.send_message(
        text=next_message,
        reply_markup=keyboard,
    )


async def process_application_answer(
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


async def pubg_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Pubg ID handler."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.warning("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    return await process_application_answer(
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
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.warning("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    return await process_application_answer(
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
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.warning("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    return await process_application_answer(
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
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.warning("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    return await process_application_answer(
        user=user,
        chat=chat,
        message=message,
        question_number=4,
        next_message="Расскажи о себе либо пропусти вопрос. Чем больше информации мы о тебе получим, тем выше вероятность одобрения заявки.",
        keyboard=keyboards.USER_SKIP_KEYBOARD,
        next_state=ApplicationStates.about_state,
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """About handler."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.warning("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    if await _is_new_answer(user, 5) is False:
        await _update_answer(user, 5, message.text)
    else:
        await _save_answer(user, 5, message.text)
    return await _show_overview(chat)


async def _show_overview(chat) -> ApplicationStates.change_or_accept_state:
    await chat.send_message(
        "Твоя заявка:\n1. pubgID\n2. возраст\n3. режимы игры\n4. Частота активности\n5. о себе\nВсе верно?",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )
    await chat.send_message(
        "1. Изменить PubgID\n2. Изменить возраст\n3. Изменить режимы игры\n4. Изменить частоту активности\n5. Изменить 'о себе'\n6. Все верно!",
        reply_markup=keyboards.USER_DECISION_KEYBOARD,
    )
    return ApplicationStates.change_or_accept_state


async def change_or_accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Change or accept handler."""
    user = update.effective_user
    chat = update.effective_chat
    if user is None or chat is None or update.message is None or context.user_data is None:
        logger.warning("Invalid user or chat or message or user_data")
        return ConversationHandler.END
    logger.debug(f"User {user} answer for change_or_accept: {update.message.text}")
    # TODO: store change_or_accept in db
    answer = update.message.text
    return await _choose_action(answer, chat, context)


async def _choose_action(answer: str | None, chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.about_state
    await chat.send_message(
        "Заявка принята!",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )
    return ConversationHandler.END
