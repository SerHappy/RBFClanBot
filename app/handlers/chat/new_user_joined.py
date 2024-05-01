from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes, ExtBot

from app.core.config import settings
from app.db.engine import UnitOfWork
from app.domain.application.exceptions import ApplicationDoesNotExistError
from app.services.applications.application_retrieve import ApplicationRetrieveService


async def new_user_joined_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Handle new user joined event.

    Args:
        update (Update): The update.
        context (ContextTypes.DEFAULT_TYPE): The context.

    Returns:
        None
    """
    message = update.message
    if not message:
        return
    logger.debug("В обработчике нового пользователя")
    new_users = message.new_chat_members
    for new_user in new_users:
        uow = UnitOfWork()
        application_service = ApplicationRetrieveService(uow)
        user_id = new_user.id
        try:
            application = await application_service.execute(user_id)
        except ApplicationDoesNotExistError:
            logger.warning(
                (
                    f"Пользователь {user_id} не имеет активной заявки. "
                    "Невозможно получить ссылку"
                ),
            )
            return
        user_link = application.invite_link
        if not user_link:
            logger.warning(
                (
                    f"Пользователь {user_id} не имеет ссылки в заявке. "
                    "Невозможно получить ссылку"
                ),
            )
            return
        await _revoke_invite_link(context.application.bot, user_link)
        logger.debug(f"Ссылка пользователя {user_id} отозвана")


async def _revoke_invite_link(bot: ExtBot, invite_link: str) -> None:
    """
    Revoke invite link.

    Args:
        bot (ExtBot): The bot.
        invite_link (str): The invite link.

    Returns:
        None
    """
    logger.debug("In revoke invite link handler.")
    chat_id = settings.CLAN_CHAT_ID
    await bot.revoke_chat_invite_link(chat_id, invite_link)
