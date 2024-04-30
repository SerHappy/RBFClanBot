from loguru import logger

from app.db.engine import UnitOfWork
from app.domain.application.entities import Application


class ApplicationFormattingService:
    """Responsible for application formatting."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize the service instance."""
        self._uow = uow

    async def execute(self, application_id: int) -> str:
        """Execute the service."""
        async with self._uow():
            application = await self._uow.application.get_by_id(application_id)
            return await self._format_application(application)

    async def _format_application(
        self,
        application: Application,
    ) -> str:
        """Возвращает текстовое представление заявки для админов."""
        logger.debug(f"Форматирование заявки для application_id={application.id}")
        status_name_escaped = self._escape_markdown(application.status)
        answers_escaped = [
            self._escape_markdown(answer.answer_text)
            for key, answer in application.answers.items()
        ]

        user_display = f"[ID{application.user_id}](tg://user?id={application.user_id})"

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
            (
                f"Форматирование заявки для {application.id=} прошло успешно, "
                f"возвращаем message={message}"
            ),
        )

        return message

    def _escape_markdown(self, text: str) -> str:
        """
        Экранирует специальные символы для MarkdownV2.

        Args:
        ----
            text: Текст для экранирования.

        Return:
        ------
            Текст с экранированными специальными символами.

        """
        logger.debug(f"Экранирование символов в тексте text={text} для MarkdownV2")
        escape_chars = "_*[]()~`>#+-=|{}.!"
        escaped_text = "".join(
            f"\\{char}" if char in escape_chars else char for char in text
        )
        logger.debug(
            (
                f"Экранирование символов в тексте {text=} прошло успешно, "
                f"новый text={escaped_text}"
            ),
        )
        return escaped_text
