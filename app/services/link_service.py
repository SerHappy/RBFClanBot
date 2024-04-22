from core.config import settings
from loguru import logger
from telegram import Bot, ChatInviteLink


async def generate_invite_link(bot: Bot) -> str:
    """
    Генерирует и возвращает ссылку на приглашение.

    Args:
        bot: Объект Bot.

    Returns:
        Ссылка на приглашение.
    """
    logger.debug("In generate invite link handler.")
    chat_id = settings.CLAN_CHAT_ID
    link: ChatInviteLink = await bot.create_chat_invite_link(chat_id, member_limit=1)
    return link.invite_link


async def revoke_invite_link(bot: Bot, invite_link: str) -> None:
    """
    Отменяет ссылку на приглашение.

    Args:
        bot: Объект Bot.
    """
    logger.debug("In revoke invite link handler.")
    chat_id = settings.CLAN_CHAT_ID
    await bot.revoke_chat_invite_link(chat_id, invite_link)
