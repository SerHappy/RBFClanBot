from db import Database
from db import Session
from loguru import logger
from models import Application


def _escape_markdown(text: str) -> str:
    """
    Экранирует специальные символы для MarkdownV2.

    Args:
        text: Текст для экранирования.

    Return:
        Текст с экранированными специальными символами.
    """
    logger.debug(f"Экранирование символов в тексте text={text} для MarkdownV2")
    escape_chars = "_*[]()~`>#+-=|{}.!"
    escaped_text = "".join(f"\\{char}" if char in escape_chars else char for char in text)
    logger.debug(
        f"Экранирование символов в тексте text={text} для MarkdownV2 прошло успешно, новый text={escaped_text}"
    )
    return escaped_text


async def format_application(application_id: Application, session: Session) -> str:
    """
    Возвращает текстовое представление заявки для админов.

    Args:
        application_id: ID заявки.
        session: Сессия базы данных.

    Returns:
        Текстовое представление заявки.
    """
    logger.debug(f"Форматирование заявки для application_id={application_id}")
    db = Database(session)
    application = await db.application.get(application_id)
    user = await db.user.get(application.user_id)
    answers = await db.application_answer.get_all_answers_by_application_id(application.id)
    status = await db.application_status.get(application.status_id)
    status_name_escaped = _escape_markdown(status.status)
    answers_escaped = [_escape_markdown(answer.answer_text) for answer in answers]

    user_display = f"[ID{user.id}](tg://user?id={user.id})"

    message = (
        f"ЗАЯВКА №{application.id} от пользователя {user_display}:\n\n"
        f"Текущий статус заявки: {status_name_escaped}\n"
        f"1\\) PUBG ID: {answers_escaped[0]}\n"
        f"2\\) Возраст: {answers_escaped[1]}\n"
        f"3\\) Режимы игры: {answers_escaped[2]}\n"
        f"4\\) Активность: {answers_escaped[3]}\n"
        f"5\\) О себе: {answers_escaped[4]}\n"
    )
    logger.debug(
        f"Форматирование заявки для application_id={application_id} прошло успешно, возвращаем message={message}"
    )

    return message
