from config import ApplicationStates
from datetime import datetime
from datetime import timedelta
from db import Database
from db import Session
from loguru import logger
from telegram import Chat
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

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
    logger.debug("Start command called.")
    user = update.effective_user
    chat = update.effective_chat

    if user is None or chat is None:
        logger.warning("User or Chat is None, skipping /start command.")
        return

    logger.debug(f"User {user} called /start")
    async with Session() as session:
        # TODO: Should be db.user.create_if_not_exists(user.id, user.username, user.first_name, user.last_name)
        # TODO: Should be db.application.create_if_not_exists(user.id)
        db = Database(session)
        await _create_user_if_not_exists(db, user.id, user.username, user.first_name, user.last_name)
        application = await db.application.get_last_application(user.id)
        now = datetime.now()

        if application is None:
            await db.application.create(user.id)
            logger.info(f"Application for user <id={user.id}> was created successfully.")
        else:
            logger.debug(f"User {user} last application: {application}")
            if application.status_id == 1:
                logger.debug(f"Deleting all answers for application <id={application.id}>")
                await db.application_answer.delete_all_answers_by_application_id(application.id)
            elif application.status_id == 2:
                await chat.send_message("Ваша заявка на рассмотрении")
                await session.commit()
                return ConversationHandler.END
            elif application.status_id == 3:
                await chat.send_message("Ваша заявка уже была принята")
                await session.commit()
                return ConversationHandler.END
            elif application.status_id == 4:
                if now - application.decision_date < timedelta(days=30):
                    await chat.send_message(
                        f"Подача повторной заявки возможна только раз в месяц. Вы сможете подать заявку {timedelta(days=30) + application.decision_date}"
                    )
                    await session.commit()
                    return ConversationHandler.END
                else:
                    await db.application.create(user.id)
                    logger.info(f"Application for user <id={user.id}> was created successfully.")
        await session.commit()

    await _send_greeting(chat)
    return await _ask_for_pubg_id(chat)


# TODO: make user data DTO for less arguments
# TODO: Move to repository
async def _create_user_if_not_exists(
    db: Database, user_id: int, username: str | None, first_name: str | None, last_name: str | None
) -> None:
    """Create user if not exists."""
    logger.debug(f"Creating user <id={user_id}> if not exists...")
    is_user_exists = await db.user.get(user_id)
    if is_user_exists is None:
        await db.user.create(user_id, username, first_name, last_name)
        logger.info(f"User <id={user_id}> was created successfully.")
        return
    logger.info(f"User <id={user_id}> found, skipping user creation...")


async def _send_greeting(chat: Chat) -> None:
    """
    Send greeting to user.

    Args:
        chat: Chat.

    Returns:
        None.
    """
    logger.debug("Sending greeting to user.")
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
    logger.debug("Asking for pubg_id.")
    await chat.send_message(
        "Напиши свой pubgID",
        reply_markup=keyboards.REMOVE_KEYBOARD,
    )
    return ApplicationStates.pubgID_state
