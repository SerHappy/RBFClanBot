from db import Database
from db import Session
from models import Application


def _escape_markdown(text: str) -> str:
    """Экранирует специальные символы для MarkdownV2."""
    escape_chars = "_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


async def format_application(application_id: Application, session: Session) -> str:
    """Возвращает текстовое представление заявки для админов."""
    db = Database(session)
    application = await db.application.get(application_id)
    user = await db.user.get(application.user_id)
    answers = await db.application_answer.get_all_answers_by_application_id(application.id)
    status = await db.application_status.get(application.status_id)
    status_name_escaped = _escape_markdown(status.status)
    answers_escaped = [_escape_markdown(answer.answer_text) for answer in answers]

    if user.username is None:
        user.username = f"[ID{user.id}](tg://user?id={user.id})"
    # Формирование сообщения
    message = (
        f"ЗАЯВКА №{application.id} от пользователя {user.username}:\n\n"
        f"Текущий статус заявки: {status_name_escaped}\n"
        f"1\\. PUBG ID: {answers_escaped[0]}\n"
        f"2\\. Возраст: {answers_escaped[1]}\n"
        f"3\\. Режимы игры: {answers_escaped[2]}\n"
        f"4\\. Активность: {answers_escaped[3]}\n"
        f"5\\. О себе: {answers_escaped[4]}\n"
    )

    return message
