from core.config import settings
from db import Database, Session
from loguru import logger
from telegram import Chat, Update
from telegram.ext import ContextTypes, ConversationHandler
from validators import question_validators


async def ban_user_preprocess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды бана пользователя."""
    chat = update.effective_chat
    if not update.message or not update.message.text or not chat:
        logger.error(
            "Получен некорректный update при попытке вызова обработчика бана пользователя."
        )
        return ConversationHandler.END
    if chat.id != settings.ADMIN_CHAT_ID:
        logger.warning("Вызов команды бана пользователя не в чате администратора.")
        return ConversationHandler.END
    user_id = update.message.text.split()[1]
    if not question_validators.is_only_numbers(user_id):
        await chat.send_message("Неверный ID пользователя.")
        return ConversationHandler.END
    await _ban_user(chat, int(user_id))


# TODO: Вынести в сервис пользователя
async def _ban_user(chat: Chat, user_id: int) -> None:
    async with Session() as session:
        db = Database(session)
        if not await db.user.get(user_id):
            await chat.send_message(f"Пользователь с ID {user_id} не существует.")
            await session.commit()
            return
        if await db.user.is_user_banned(user_id):
            await chat.send_message(f"Пользователь с ID {user_id} уже забанен.")
            await session.commit()
            return
        await db.user.ban_user(user_id)
        await session.commit()
    await chat.send_message(f"Пользователь с ID {user_id} забанен.")
