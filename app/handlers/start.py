from config import ApplicationStates
from db import Database
from db import Session
from loguru import logger
from telegram import Chat
from telegram import Update
from telegram.ext import ContextTypes

import keyboards


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> ApplicationStates.pubgID_state:
    """
    Start command handler. Start fsm for application creation.

    Args:
        update: Update object.
        context: Context.

    Returns:
        new FSM state ApplicationStates.pubgID_state.
    """
    user = update.effective_user
    chat = update.effective_chat

    if user is None or chat is None:
        logger.warning("User or Chat is None, skipping /start command.")
        return

    logger.debug(f"User {user} called /start")
    async with Session() as session:
        # Should be db.user.create_if_not_exists(user.id, user.username, user.first_name, user.last_name)
        # Should be db.application.create_if_not_exists(user.id)
        db = Database(session)
        await _create_user_if_not_exists(db, user.id, user.username, user.first_name, user.last_name)
        await _create_application_if_not_exists(db, user.id)
        await session.commit()

    await _send_greeting(chat)
    return await _ask_for_pubg_id(chat)


# TODO: make user data DTO for less arguments
# TODO: Move to repository
async def _create_user_if_not_exists(
    db: Database, user_id: int, username: str | None, first_name: str | None, last_name: str | None
) -> None:
    """Create user if not exists."""
    is_user_exists = await db.user.get(user_id)
    if is_user_exists is None:
        await db.user.create(user_id, username, first_name, last_name)
        logger.info(f"User <id={user_id}> was created successfully.")
        return
    logger.info(f"User <id={user_id}> found, skipping user creation...")


# TODO: Move to repository
async def _create_application_if_not_exists(db: Database, user_id: int):
    """Create application if not exists."""
    is_application_exists = await db.application.get_last_application(user_id)
    if is_application_exists is None:
        await db.application.create(user_id)
        logger.info(f"Application for user <id={user_id}> was created successfully.")
        return
    logger.info(f"Application for user <id={user_id}> found, skipping application creation...")


async def _send_greeting(chat: Chat) -> None:
    """
    Send greeting to user.

    Args:
        chat: Chat.

    Returns:
        None.
    """
    await chat.send_message(
        "Приветствую!\nДля вступления в клан надо заполнить заявку. Будь готов ответить на 5 вопросов!\n",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )


async def _ask_for_pubg_id(chat: Chat) -> ApplicationStates.pubgID_state:
    """
    Ask for pubg_id. Change state to pubg_id_state.

    Args:
        chat: Chat.

    Returns:
        new FSM state ApplicationStates.pubgID_state.
    """
    await chat.send_message(
        "Напиши свой pubgID",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )
    return ApplicationStates.pubgID_state
