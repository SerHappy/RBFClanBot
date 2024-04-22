import keyboards
from config import ApplicationStates
from db import Database, session_factory
from loguru import logger
from telegram import (
    Chat,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import ContextTypes


async def process_application_answer(
    user_id: int,
    chat: Chat,
    message: Message,
    question_number: int,
    next_message: str,
    keyboard: ReplyKeyboardMarkup | ReplyKeyboardRemove | InlineKeyboardMarkup,
    next_state: ApplicationStates,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """
    Процедура обработки ответа на вопрос анкеты.

    Args:
        user: Экземпляр User.
        chat: Экземпляр Chat.
        message: Экземпляр Message.
        question_number: Номер вопроса.
        next_message: Текст следующего вопроса.
        keyboard: Клавиатура.
        next_state: Следующее состояние.

    Returns:
        Новое состояние.
    """
    logger.debug(
        f"Обработка ответа на вопрос question_number={question_number} для пользователя user={user_id}"
    )
    if (
        await _is_new_answer(user_id, question_number) is False
        and context.user_data["application_completed"] is True
    ):  # type: ignore
        logger.debug(
            f"Пользователь user={user_id} уже отвечал на вопрос question_number={question_number}, обновляем"
        )
        await _update_answer(user_id, question_number, message.text)
        logger.debug(f"Показываем овервью анкеты для пользователя user={user_id}")
        return await show_overview(chat)
    logger.debug(
        f"Пользователь user={user_id} еще не отвечал на вопрос question_number={question_number}, сохраняем"
    )
    await _save_answer(user_id, question_number, message.text)
    await ask_next_question(chat, next_message, keyboard)
    logger.debug(
        f"Возвращаем следующее состояние next_state={next_state} для пользователя user={user_id}"
    )
    return next_state


async def show_overview(chat: Chat) -> ApplicationStates.change_or_accept_state:
    """
    Показать обзор заявки и предложить изменить или принять заявку.

    Args:
        chat: Чат.

    Returns:
        Новое состояние ApplicationStates.change_or_accept_state.
    """
    logger.info(f"Показать обзор заявки для chat_id={chat.id}")
    async with session_factory() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        application = await db.application.get_active_application(user_id=chat.id)
        answers = await db.application_answer.get_all_answers_by_application_id(
            application.id
        )
    await chat.send_message(
        f"Твоя заявка:\n\n1) PUBG ID: {answers[0].answer_text}\n2) Возраст: {answers[1].answer_text}\n3) Режимы игры: {answers[2].answer_text}\n4) Активность: {answers[3].answer_text}\n5) О себе: {answers[4].answer_text}\n\nВсе верно?",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )
    logger.debug(f"Показан обзор заявки для chat_id={chat.id}")
    await chat.send_message(
        "1) Изменить PubgID\n2) Изменить возраст\n3) Изменить режимы игры\n4) Изменить частоту активности\n5) Изменить 'о себе'\n6) Все верно!",
        reply_markup=keyboards.USER_DECISION_KEYBOARD,
    )
    logger.debug(f"Показаны варианты ответа для chat_id={chat.id}")
    return ApplicationStates.change_or_accept_state


async def _is_new_answer(user_id: int, question_number: int) -> bool:
    """
    Проверка на новый ответ для пользователя.

    Args:
        user: Пользователь.
        question_number: Номер вопроса.

    Returns:
        True, если новый ответ, False, если нет.

    """
    logger.debug(
        f"Проверка на новый ответ для пользователя user={user_id} для вопроса question_number={question_number}"
    )
    async with session_factory() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        user_application = await db.application.get_active_application(user_id)
        user_answer = (
            await db.application_answer.get_application_answer_text_by_question_number(
                user_application.id, question_number
            )
        )
        if user_answer is not None:
            logger.debug(
                f"Пользователь user={user_id} уже отвечал на вопрос question_number={question_number}"
            )
            return False
        logger.debug(
            f"Пользователь user={user_id} еще не отвечал на вопрос question_number={question_number}"
        )
        return True


async def _save_answer(user_id: int, question_number: int, answer: str | None) -> None:
    """
    Сохранение ответа на вопрос.

    Args:
        user: Пользователь.
        question_number: Номер вопроса.
        answer: Текст ответа.

    Returns:
        None
    """
    logger.info(
        f"Сохранение ответа answer={answer} для пользователя user_id={user_id} для вопроса question_number={question_number}"
    )
    async with session_factory() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        user_application = await db.application.get_active_application(user_id)
        await db.application_answer.create(user_application.id, question_number, answer)
        logger.debug(
            f"Ответ пользователя user_id={user_id} для вопроса question_number={question_number} анкеты application_id={user_application.id} сохранен"
        )
        await session.commit()


async def _update_answer(
    user_id: int, question_number: int, answer: str | None
) -> None:
    """
    Обновление ответа на вопрос.

    Args:
        user: Пользователь.
        question_number: Номер вопроса.
        answer: Текст ответа.

    Returns:
        None
    """
    logger.debug(
        f"Обновление ответа answer={answer} для пользователя user_id={user_id} для вопроса question_number={question_number}"
    )
    async with session_factory() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        user_application = await db.application.get_active_application(user_id)
        await db.application_answer.update_question_answer(
            user_application.id, question_number, answer
        )
        logger.debug(
            f"Ответ пользователя user_id={user_id} для вопроса question_number={question_number} анкеты application_id={user_application.id} обновлен на answer={answer}"
        )
        await session.commit()


async def ask_next_question(
    chat: Chat,
    next_message: str,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup | ReplyKeyboardRemove,
) -> None:
    """
    Задать следующий вопрос.

    Args:
        chat: Чат.
        next_message: Текст следующего вопроса.
        keyboard: Клавиатура.

    Returns:
        None
    """
    logger.debug(
        f"Отправляем следующий вопрос question_message={next_message} в чат chat_id={chat.id}"
    )
    await chat.send_message(
        text=next_message,
        reply_markup=keyboard,
    )


async def change_application_status_to_waiting(user_id: int) -> None:
    """
    Изменяем статус заявки на "ожидание".

    Args:
        user: Пользователь.

    Returns:
        None
    """
    logger.debug(f"Изменяем статус заявки на ожидание для пользователя user={user_id}")
    async with session_factory() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        user_application = await db.application.get_active_application(user_id)
        await db.application.change_status(user_application.id, 2)
        await session.commit()
        logger.debug(
            f"Статус заявки для пользователя user={user_id} изменен на ожидание"
        )
