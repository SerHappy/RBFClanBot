from decouple import config
from loguru import logger
from telegram import Bot
from telegram import ChatInviteLink


async def generate_invite_link(bot: Bot) -> str:
    """
    Генерирует и возвращает ссылку на приглашение.

    Args:
        bot: Объект Bot.

    Returns:
        Ссылка на приглашение.
    """
    logger.debug("In generate invite link handler.")
    chat_id = config("CLAN_CHAT_ID", cast=int)
    link: ChatInviteLink = await bot.create_chat_invite_link(chat_id, member_limit=1)
    return link.invite_link
