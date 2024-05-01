import asyncio

from loguru import logger
from telegram import Message, error
from telegram.ext import ExtBot

from app.infra.messaging.exceptions import MaxRetriesError


class MessageSendingService:
    """Represents a service for sending messages to the user."""

    def __init__(self, bot: ExtBot, max_retries: int = 5, delay: int = 1) -> None:
        """
        Initialize the message sending service.

        Args:
            bot (ExtBot): The bot instance.
            max_retries (int, optional): The maximum number of retries. Defaults to 5.
            delay (int, optional): The delay between retries. Defaults to 1.

        Returns:
            None
        """
        self.bot = bot
        self.max_retries = max_retries
        self.delay = delay

    async def send_message(self, chat_id: int, text: str) -> Message:
        """
        Send a message to the user.

        Args:
            chat_id (int): The chat ID of the user.
            text (str): The text of the message.

        Returns:
            Message: The sent message.
        """
        for attempt in range(self.max_retries):
            try:
                message = await self.bot.send_message(chat_id=chat_id, text=text)
            except error.RetryAfter as e:  # noqa: PERF203
                await asyncio.sleep(e.retry_after)
            except error.ChatMigrated as e:
                logger.critical(
                    "Chat migrated: %s. Shutting down. Check error and restart bot",
                    e,
                )
                await self.bot.shutdown()
            except error.Forbidden:
                logger.warning(
                    "Bot is not allowed to send messages. Chat id: %s",
                    chat_id,
                )
                raise
            except (error.BadRequest, error.InvalidToken) as e:
                logger.critical(
                    (
                        "Failed to send message: %s. Shutting down."
                        "Check error and restart bot"
                    ),
                    e,
                )
                await self.bot.shutdown()
            except error.TelegramError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.delay)
                else:
                    logger.error(
                        (
                            "Failed to send message after"
                            f"{self.max_retries} attempts: {e}"
                        ),
                    )
                    raise
            else:
                return message
        raise MaxRetriesError
