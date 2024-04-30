from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.core.config import settings
from app.db.engine import UnitOfWork
from app.domain.user.exceptions import UserIsNotBannedError, UserNotFoundError
from app.services.users.user_unban import UserUnbanService
from app.validators import question_validators


async def unban_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> int | None:
    """Обработчик команды бана пользователя."""
    chat = update.effective_chat
    if not update.message or not update.message.text or not chat:
        logger.error(
            (
                "Получен некорректный update при попытке "
                "вызова обработчика анбана пользователя."
            ),
        )
        return ConversationHandler.END
    if chat.id != settings.ADMIN_CHAT_ID:
        logger.warning("Вызов команды разбана пользователя не в чате администратора.")
        return ConversationHandler.END
    user_id = update.message.text.split()[1]
    if not question_validators.is_only_numbers(user_id):
        await chat.send_message("Неверный ID пользователя.")
        return ConversationHandler.END
    uow = UnitOfWork()
    unban_service = UserUnbanService(uow)
    try:
        await unban_service.execute(int(user_id))
    except UserNotFoundError:
        await chat.send_message("Пользователь не найден.")
    except UserIsNotBannedError:
        await chat.send_message("Пользователь не забанен.")
    else:
        await chat.send_message("Пользователь разбанен.")
    return None
