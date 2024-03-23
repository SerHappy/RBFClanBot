from decouple import config
from loguru import logger
from telegram.ext import ApplicationBuilder

import handlers


def main() -> None:
    """
    Энтрипоинт для запуска бота.

    Запускает бота с помощью long-polling в event loop.
    """
    application = ApplicationBuilder().token(config("BOT_TOKEN", cast=str)).build()
    logger.debug("Создание приложения прошло успешно.")
    handlers.add_all_handlers(application)
    logger.debug("Добавление обработчиков прошло успешно.")
    logger.info("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()
