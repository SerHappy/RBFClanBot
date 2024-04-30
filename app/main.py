from pathlib import Path

import uvloop
from loguru import logger
from telegram.ext import Application, ApplicationBuilder

from app import handlers
from app.core.config import settings
from app.handlers import error


def main() -> None:
    """Энтрипоинт приложения."""
    _loguru_setup()
    _install_uvloop()
    _start_bot()


def _loguru_setup() -> None:
    """Настройка логгера."""
    logger.remove()
    current_file_path = Path(__file__).resolve()
    app_directory = current_file_path.parent
    logs_directory = app_directory / "logs"
    Path.mkdir(logs_directory, exist_ok=True)
    full_log_path = logs_directory / "full_log.log"
    warnings_log_path = logs_directory / "warnings_and_above.log"
    logger.add(
        sink=full_log_path,
        level="DEBUG",
        rotation="1 day",
        compression="zip",
    )
    logger.add(
        sink=warnings_log_path,
        level="WARNING",
        rotation="10 MB",
        compression="zip",
    )
    logger.info("Настройка логгера прошла успешно.")


def _install_uvloop() -> None:
    """Установка uvloop как event loop по умолчанию."""
    uvloop.install()
    logger.debug("Установка uvloop прошла успешно.")


async def post_init(application: Application) -> None:
    """Установка команд для бота."""
    await application.bot.set_my_commands([("start", "Подать заявку")])


def _start_bot() -> None:
    """Запуск бота."""
    application: Application = (
        ApplicationBuilder().token(settings.BOT_TOKEN).post_init(post_init).build()
    )
    logger.debug("Создание приложения прошло успешно.")
    handlers.add_all_handlers(application)
    application.add_error_handler(error.error_handler)
    logger.debug("Добавление обработчиков прошло успешно.")
    logger.info("Бот запущен")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
