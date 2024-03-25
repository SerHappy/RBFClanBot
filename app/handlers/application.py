from config import ApplicationStates
from datetime import datetime
from datetime import timedelta
from db import Database
from db import Session
from loguru import logger
from models.applications import Application
from services import sender
from telegram import Bot
from telegram import Chat
from telegram import constants
from telegram import InlineKeyboardMarkup
from telegram import Message
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram import User
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

import keyboards


# TODO: ПЕРЕПИСАТЬ ЭТО, ИСПОЛЬЗУЯ НЕСКОЛЬКО ФАЙЛОВ, ОТДЕЛЬНЫЙ МОДУЛЬ


async def start_command(
    update: Update,
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
    if update.edited_message:
        return
    user = update.effective_user
    chat = update.effective_chat

    # TODO: Вынести это в middleware
    if user is None or chat is None:
        logger.critical(
            "Пользователь или чат не определены при вызове команды /start! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END

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
        application = await application_repo.create_if_not_exists(db_user.id)

        result = await handle_application_logic(application, chat, session)

        await session.commit()

    if result == ConversationHandler.END:
        logger.info(f"Пользователь chat_id={chat.id} не может заполнять анкету , выход из /start")
        return ConversationHandler.END
    context.user_data["application_completed"] = False  # type: ignore
    logger.debug("Создана переменная application_completed, значение которой равно False")
    logger.info(
        f"Пользователь chat_id={chat.id} начинает заполнять анкету, переводим в состояние {ApplicationStates.pubgID_state}"
    )
    await _send_greeting(chat)
    return await _ask_for_pubg_id(chat)


# TODO: Вынести в отдельный модуль логики
async def handle_application_logic(application: Application, chat: Chat, session: Session) -> int | None:
    """
    Обработчик логики заявки.

    Args:
        application: Заявка.
        chat: Чат.
        session: Сессия базы данных.

    Returns:
        Переводит в состояние ConversationHandler.END или None.
    """
    db = Database(session)

    if application.status_id == 1:
        logger.debug(f"Пользователь user_id={application.user_id} заново заполняет анкету")
        await db.application_answer.delete_all_answers_by_application_id(application.id)
        return None
    if application.status_id == 2:
        logger.debug(
            f"Заявка пользователя application_id={application.user_id} на рассмотрении, FSM заполнения анкеты не запускается"
        )
        await chat.send_message("Ваша заявка на рассмотрении")
        return ConversationHandler.END
    if application.status_id == 3:
        logger.debug(
            f"Заявка пользователя application_id={application.user_id} уже принята, FSM заполнения анкеты не запускается"
        )
        await chat.send_message("Ваша заявка уже была принята")
        return ConversationHandler.END
    if application.status_id == 4:
        now = datetime.now()
        if now - application.decision_date < timedelta(days=30):
            logger.debug(
                f"Пользователь user_id={application.user_id} пытается подать заявку повторно, но еще не прошло 30 дней, FSM заполнения анкеты не запускается"
            )
            await chat.send_message(
                f"Подача повторной заявки возможна только раз в месяц.\nВы сможете подать заявку {(timedelta(days=30) + application.decision_date).strftime('%d.%m.%Y %H:%M')} (UTC+0)."
            )
            return ConversationHandler.END
        logger.debug(
            f"Пользователь user_id={application.user_id} пытается подать заявку повторно, 30 дней прошло, FSM заполнения анкеты запускается"
        )
        await db.application.create(chat.id)
    return None


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


def _is_correct_pubg_id(pubg_id: str | None) -> bool:
    """
    Проверка корректности pubg_id.

    Корректный pubg_id состоит из цифр.

    Args:
        pubg_id: PUBG ID.

    Returns:
        True, если pubg_id корректен, False в противном случае.
    """
    if pubg_id is None:
        return False
    return all(character in "0123456789" for character in pubg_id)


async def pubg_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.pubgID_state.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Это же состояние, если проверка корректности pubg_id не пройдена, иначе следующее состояние.

    """
    if update.edited_message:
        return ApplicationStates.pubgID_state
    user = update.effective_user
    chat = update.effective_chat
    print(update, user, chat, sep="\n")
    message = update.message
    if user is None or chat is None or message is None:
        logger.critical(
            "Получен некорректный user или chat или message в обработчике pubg_id! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END

    logger.info(f"Пользователь chat_id={chat.id} ответил на вопрос pubg_id: {message.text}")

    if not _is_correct_pubg_id(message.text):
        logger.debug(f"Получен некорректный pubg_id={message.text} в чате chat_id={chat.id}.")
        await chat.send_message("Проверьте правильность ввода pubg_id. Pubg_id должен состоять только из цифр.")
        return ApplicationStates.pubgID_state

    return await _process_application_answer(
        user=user,
        chat=chat,
        message=message,
        question_number=1,
        next_message="Сколько тебе полных лет?",
        keyboard=keyboards.REMOVE_KEYBOARD,
        next_state=ApplicationStates.age_state,
        context=context,
    )


def _is_correct_age(message: str | None) -> bool:
    """Проверка корректности возраста.

    Возраст должен быть целым числом от 1 до 100.

    Args:
        message: Возраст.

    Returns:
        True, если возраст корректен, False в противном случае.

    """
    if message is None:
        return False
    if not message.isdigit():
        return False
    if int(message) < 1 or int(message) > 100:
        return False
    return True


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.old_state.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Это же состояние, если проверка корректности возраста не пройдена, иначе следующее состояние.

    """
    if update.edited_message:
        return ApplicationStates.age_state
    user = update.effective_user
    chat = update.effective_chat
    message = update.message

    if user is None or chat is None or message is None:
        logger.critical(
            "Получен некорректный user или chat или message в обработчике age! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END

    logger.info(f"Пользователь chat_id={chat.id} ответил на вопрос age: {message.text}")

    if not _is_correct_age(message.text):
        logger.debug(f"Получен некорректный age={message.text} в чате chat_id={chat.id}.")
        await chat.send_message("Проверьте правильность ввода возраста. Возраст должен быть целым числом от 1 до 100.")
        return ApplicationStates.age_state

    return await _process_application_answer(
        user=user,
        chat=chat,
        message=message,
        question_number=2,
        next_message="Какие режимы игры предпочитаешь больше всего? (можно несколько)",
        keyboard=keyboards.REMOVE_KEYBOARD,
        next_state=ApplicationStates.game_modes_state,
        context=context,
    )


# TODO: Добавить ограничение символов в ответе
async def game_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.game_modes_state.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Следующее состояние.

    """
    if update.edited_message:
        return ApplicationStates.game_modes_state
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.critical(
            "Получен некорректный user или chat или message в обработчике game_mode! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END

    logger.info(f"Пользователь chat_id={chat.id} ответил на вопрос game_mode: {message.text}")

    return await _process_application_answer(
        user=user,
        chat=chat,
        message=message,
        question_number=3,
        next_message="Сколько времени в день готов уделять игре с соклановцами? (примерно; можно по дням)",
        keyboard=keyboards.REMOVE_KEYBOARD,
        next_state=ApplicationStates.activity_state,
        context=context,
    )


# TODO: Добавить ограничение символов в ответе
async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.activity_state.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Следующее состояние.

    """
    if update.edited_message:
        return ApplicationStates.activity_state
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.critical(
            "Получен некорректный user или chat или message в обработчике activity! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END

    logger.info(f"Пользователь chat_id={chat.id} ответил на вопрос activity: {message.text}")

    return await _process_application_answer(
        user=user,
        chat=chat,
        message=message,
        question_number=4,
        next_message="Расскажи о себе, либо пропусти вопрос.\n"
        + "Чем больше информации мы о тебе получим, тем выше вероятность одобрения заявки.",
        keyboard=keyboards.USER_SKIP_KEYBOARD,
        next_state=ApplicationStates.about_state,
        context=context,
    )


async def about_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.about_state при вводе "Пропустить".

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Следующее состояние. Показ обзора анкеты.
    """
    if update.edited_message:
        return ApplicationStates.about_state
    user = update.effective_user
    chat = update.effective_chat
    answer = "Пусто"

    if user is None or chat is None:
        logger.critical(
            "Получен некорректный user или chat в обработчике about_skip! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END

    logger.info(f"Пользователь chat_id={chat.id} ответил на вопрос about: {answer}")

    if await _is_new_answer(user, 5) is False and context.user_data["application_completed"] is True:  # type: ignore
        logger.debug(f"Пользователь user={user} уже отвечал на вопрос about_skip, обновляем его ответ")
        await _update_answer(user, 5, answer)
    else:
        logger.debug(f"Пользователь user={user} еще не отвечал на вопрос about_skip, сохраняем его ответ")
        await _save_answer(user, 5, answer)
    logger.info(f"Показать обзор заявки для chat_id={chat.id}")
    return await _show_overview(chat)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка ответа состояния ApplicationStates.about_state при вводе текста о себе.

    Args:
        update: Экземпляр Update.
        context: Контекст.

    Returns:
        Следующее состояние. Показ обзора анкеты.
    """
    if update.edited_message:
        return ApplicationStates.about_state
    logger.debug("Starting handle about answer")
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    if user is None or chat is None or message is None:
        logger.critical(
            "Получен некорректный user или chat или message в обработчике activity! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END

    logger.info(f"Пользователь chat_id={chat.id} ответил на вопрос about: {message.text}")

    if await _is_new_answer(user, 5) is False and context.user_data["application_completed"] is True:  # type: ignore
        logger.debug(f"Пользователь user={user} уже отвечал на вопрос about, обновляем его ответ")
        await _update_answer(user, 5, message.text)
    else:
        logger.debug(f"Пользователь user={user} еще не отвечал на вопрос about, сохраняем его ответ")
        await _save_answer(user, 5, message.text)
    logger.info(f"Показать обзор заявки для chat_id={chat.id}")
    return await _show_overview(chat)


async def _show_overview(chat: Chat) -> ApplicationStates.change_or_accept_state:
    """
    Показать обзор заявки и предложить изменить или принять заявку.

    Args:
        chat: Чат.

    Returns:
        Новое состояние ApplicationStates.change_or_accept_state.
    """
    logger.info(f"Показать обзор заявки для chat_id={chat.id}")
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        application = await db.application.get_active_application(user_id=chat.id)
        answers = await db.application_answer.get_all_answers_by_application_id(application.id)
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


async def user_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    if update.edited_message:
        return ApplicationStates.change_or_accept_state
    user = update.effective_user
    chat = update.effective_chat
    answer = update.message
    if user is None or chat is None or answer is None:
        logger.critical(
            "Получен некорректный user или chat или answer в обработчике user_decision! Данная ошибка не должна никогда происходить."
        )
        return ConversationHandler.END

    logger.info(f"Обработка варианта ответа пользователя для chat_id={chat.id}")

    context.user_data["application_completed"] = True  # type: ignore
    logger.debug(f"Переменная application_completed для chat_id={chat.id} установлена в True")

    logger.info(f"Пользователь chat_id={chat.id} ответил на вопрос overview: {answer.text}")

    return await _choose_action(answer.text, user, chat, context)


async def _choose_action(answer: str | None, user: User, chat: Chat, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    logger.debug(f"Выбор действия для пользователя user={user}")
    if answer == "1":
        logger.debug(f"Пользователь user={user} выбрал изменить PubgID")
        await _ask_next_question(
            chat,
            "Напиши свой PUBG ID",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.pubgID_state
    if answer == "2":
        logger.debug(f"Пользователь user={user} выбрал изменить возраст")
        await _ask_next_question(
            chat,
            "Напиши свой возраст",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.age_state
    if answer == "3":
        logger.debug(f"Пользователь user={user} выбрал изменить режимы игры")
        await _ask_next_question(
            chat,
            "Какие режимы игры предпочитаешь больше всего? (можно несколько)",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.game_modes_state
    if answer == "4":
        logger.debug(f"Пользователь user={user} выбрал изменить частоту активности")
        await _ask_next_question(
            chat,
            "Сколько времени в день готов уделять игре с соклановцами?",
            keyboards.REMOVE_KEYBOARD,
        )
        return ApplicationStates.activity_state
    if answer == "5":
        logger.debug(f"Пользователь user={user} выбрал изменить о себе")
        await _ask_next_question(
            chat,
            "Расскажи о себе либо пропусти вопрос. Чем больше информации мы о тебе получим, тем выше вероятность одобрения заявки.",
            keyboards.USER_SKIP_KEYBOARD,
        )
        return ApplicationStates.about_state
    if answer == "6":
        logger.debug(f"Пользователь user={user} выбрал отправить заявку администраторам")
        await _change_application_status_to_waiting(user)
        await chat.send_message(
            "Заявка отправлена, ожидайте ответа!",
            reply_markup=keyboards.REMOVE_KEYBOARD,
        )
        await sender.send_application_to_admins(bot=context.bot, user_id=user.id)
        return ConversationHandler.END
    logger.debug(f"Пользователь user={user} ввел неверную команду")
    await chat.send_message("Неверная команда. Выберите число от 1 до 6.")
    return ApplicationStates.change_or_accept_state


async def _process_application_answer(
    user: User,
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
    logger.debug(f"Обработка ответа на вопрос question_number={question_number} для пользователя user={user}")
    if await _is_new_answer(user, question_number) is False and context.user_data["application_completed"] is True:  # type: ignore
        logger.debug(f"Пользователь user={user} уже отвечал на вопрос question_number={question_number}, обновляем")
        await _update_answer(user, question_number, message.text)
        logger.debug(f"Показываем овервью анкеты для пользователя user={user}")
        return await _show_overview(chat)
    logger.debug(f"Пользователь user={user} еще не отвечал на вопрос question_number={question_number}, сохраняем")
    await _save_answer(user, question_number, message.text)
    await _ask_next_question(chat, next_message, keyboard)
    logger.debug(f"Возвращаем следующее состояние next_state={next_state} для пользователя user={user}")
    return next_state


async def _change_application_status_to_waiting(user: User) -> None:
    """
    Изменяем статус заявки на "ожидание".

    Args:
        user: Пользователь.

    Returns:
        None
    """
    logger.debug(f"Изменяем статус заявки на ожидание для пользователя user={user}")
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        user_application = await db.application.get_active_application(user.id)
        await db.application.change_status(user_application.id, 2)
        await session.commit()
        logger.debug(f"Статус заявки для пользователя user={user} изменен на ожидание")


async def _is_new_answer(user: User, question_number: int) -> bool:
    """
    Проверка на новый ответ для пользователя.

    Args:
        user: Пользователь.
        question_number: Номер вопроса.

    Returns:
        True, если новый ответ, False, если нет.

    """
    logger.debug(f"Проверка на новый ответ для пользователя user={user} для вопроса question_number={question_number}")
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        user_application = await db.application.get_active_application(user.id)
        user_answer = await db.application_answer.get_application_answer_text_by_question_number(
            user_application.id, question_number
        )
        if user_answer is not None:
            logger.debug(f"Пользователь user={user} уже отвечал на вопрос question_number={question_number}")
            return False
        logger.debug(f"Пользователь user={user} еще не отвечал на вопрос question_number={question_number}")
        return True


async def _save_answer(user: User, question_number: int, answer: str | None) -> None:
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
        f"Сохранение ответа answer={answer} для пользователя user_id={user.id} для вопроса question_number={question_number}"
    )
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        user_application = await db.application.get_active_application(user.id)
        await db.application_answer.create(user_application.id, question_number, answer)
        logger.debug(
            f"Ответ пользователя user_id={user.id} для вопроса question_number={question_number} анкеты application_id={user_application.id} сохранен"
        )
        await session.commit()


async def _update_answer(user: User, question_number: int, answer: str | None) -> None:
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
        f"Обновление ответа answer={answer} для пользователя user_id={user.id} для вопроса question_number={question_number}"
    )
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        user_application = await db.application.get_active_application(user.id)
        await db.application_answer.update_question_answer(user_application.id, question_number, answer)
        logger.debug(
            f"Ответ пользователя user_id={user.id} для вопроса question_number={question_number} анкеты application_id={user_application.id} обновлен на answer={answer}"
        )
        await session.commit()


async def _ask_next_question(
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
    logger.debug(f"Отправляем следующий вопрос question_message={next_message} в чат chat_id={chat.id}")
    await chat.send_message(
        text=next_message,
        reply_markup=keyboard,
    )


async def handle_admin_decision(application_id: int, bot: Bot) -> None:
    """
    Обработка решения админа.

    Args:
        application_id: ID заявки.
        bot: Телеграм бот.

    Returns:
        None
    """
    logger.info(f"Обработка решения админа application_id={application_id}")
    async with Session() as session:
        logger.debug("Подключение к базе данных прошло успешно")
        db = Database(session)
        application = await db.application.get(application_id)
        application_status = application.status_id
        if application_status == 3:
            logger.debug(f"Заявка application_id={application_id} принята, уведомляем пользователя и отправляем инвайт")
            await bot.send_message(
                chat_id=application.user_id,
                text="Ваша заявка принята!\nВаша персональная ссылка: {}".format(application.invite_link),
            )
        elif application_status == 4:
            logger.debug(
                f"Заявка application_id={application_id} отклонена, уведомляем пользователя и отправляем причину отказа"
            )
            await bot.send_message(
                chat_id=application.user_id,
                text="Ваша заявка отклонена.\nПричина отказа: {}.\nПопробуйте снова {} (UTC+0).".format(
                    application.rejection_reason,
                    (timedelta(days=30) + application.decision_date).strftime("%d.%m.%Y %H:%M"),
                ),
            )
        await bot.send_message(
            chat_id=application.user_id,
            text="Если у вас есть какие-то вопросы или предложения по улучшению, напишите @RBFManager",
        )
        await session.commit()
