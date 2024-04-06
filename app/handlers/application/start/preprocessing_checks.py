from datetime import datetime
from datetime import timedelta
from db import Database
from db import Session
from loguru import logger
from models.applications import Application
from telegram import Chat

import keyboards


async def check_user_ability_to_fill_application(user_id: int, chat: Chat, session: Session) -> bool:
    """Проверка возможности заполнения анкеты."""
    if await is_user_able_to_start(user_id, chat, session):
        return await _check_application_status(user_id, chat, session)
    return False


async def is_user_able_to_start(user_id: int, chat: Chat, session: Session) -> bool:
    """Проверка забанен ли пользователь."""
    db = Database(session)
    if await db.user.is_user_banned(user_id):
        logger.debug(f"Пользователь user_id={user_id} забанен, заполнение анкеты невозможно")
        await chat.send_message("Вы забанены. Заполнение анкеты невозможно", reply_markup=keyboards.REMOVE_KEYBOARD)
        return False
    return True


async def _check_application_status(user_id: int, chat: Chat, session: Session) -> bool:
    """
    Проверка статуса заявки.

    Args:
        application: Заявка.
        chat: Чат.
        session: Сессия базы данных.

    Returns:
        True если статус позволяет создать заявку, иначе False.
    """
    db = Database(session)

    application: Application = await db.application.get_active_application(user_id)

    if application.status_id == 1:
        logger.debug(f"Пользователь user_id={application.user_id} заново заполняет анкету")
        await db.application_answer.delete_all_answers_by_application_id(application.id)
        return True
    if application.status_id == 2:
        logger.debug(
            f"Заявка пользователя application_id={application.user_id} на рассмотрении, FSM заполнения анкеты не запускается"
        )
        await chat.send_message(
            "Ваша заявка на рассмотрении",
            reply_markup=keyboards.REMOVE_KEYBOARD,
        )
        return False
    if application.status_id == 3:
        logger.debug(
            f"Заявка пользователя application_id={application.user_id} уже принята, FSM заполнения анкеты не запускается"
        )
        await chat.send_message(
            "Ваша заявка уже была принята",
            reply_markup=keyboards.REMOVE_KEYBOARD,
        )
        return False
    if application.status_id == 4:
        now = datetime.now()
        if now - application.decision_date < timedelta(days=30):
            logger.debug(
                f"Пользователь user_id={application.user_id} пытается подать заявку повторно, но еще не прошло 30 дней, FSM заполнения анкеты не запускается"
            )
            await chat.send_message(
                f"Подача повторной заявки возможна только раз в месяц.\nВы сможете подать заявку {(timedelta(days=30) + application.decision_date).strftime('%d.%m.%Y %H:%M')} (UTC+0).",
                reply_markup=keyboards.REMOVE_KEYBOARD,
            )
            return False
        logger.debug(
            f"Пользователь user_id={application.user_id} пытается подать заявку повторно, 30 дней прошло, FSM заполнения анкеты запускается"
        )
        await db.application.create(chat.id)
        return True
    return False
