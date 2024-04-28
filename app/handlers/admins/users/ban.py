from core.config import settings
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from validators import question_validators

from app.db.engine import UnitOfWork
from app.domain.user.exceptions import UserIsBannedError, UserNotFoundError
from app.services.users.user_ban import UserBanService


async def ban_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> int | None:
    """Обработчик команды бана пользователя."""
    chat = update.effective_chat
    if not update.message or not update.message.text or not chat:
        logger.error(
            (
                "Получен некорректный update при попытке "
                "вызова обработчика бана пользователя."
            ),
        )
        return ConversationHandler.END
    if chat.id != settings.ADMIN_CHAT_ID:
        logger.warning("Вызов команды бана пользователя не в чате администратора.")
        return ConversationHandler.END
    user_id = update.message.text.split()[1]
    if not question_validators.is_only_numbers(user_id):
        await chat.send_message("Неверный ID пользователя.")
        return ConversationHandler.END
    uow = UnitOfWork()
    ban_service = UserBanService(uow)
    try:
        await ban_service.execute(int(user_id))
    except UserNotFoundError:
        await chat.send_message("Пользователь не найден.")
    except UserIsBannedError:
        await chat.send_message("Пользователь уже забанен.")
    else:
        await chat.send_message("Пользователь забанен.")
    return None
