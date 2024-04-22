from db import Database, Session
from loguru import logger
from services import link_service
from telegram import Update
from telegram.ext import ContextTypes


async def new_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нового пользователя."""
    message = update.message
    if not message:
        return
    logger.debug("В обработчике нового пользователя")
    new_users = message.new_chat_members
    for new_user in new_users:
        user_id = new_user.id
        async with Session() as session:
            db = Database(session)
            application = await db.application.get_active_application(user_id)
            if not application:
                logger.warning(f"Пользователь {user_id} не имеет активной заявки. Невозможно получить ссылку")
                return
            user_link = application.invite_link
            if not user_link:
                logger.warning(f"Пользователь {user_id} не имеет ссылки в заявке. Невозможно получить ссылку")
                return
            await link_service.revoke_invite_link(context.application.bot, user_link)
            logger.debug(f"Ссылка пользователя {user_id} отозвана")
