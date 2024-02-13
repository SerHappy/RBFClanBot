from decouple import config
from loguru import logger
from telegram.ext import ApplicationBuilder

import handlers


# custom_formatter = CustomFormatter(fmt="%(asctime)s - %(levelname)s - %(message)s")
# logger.handlers[0].setFormatter(custom_formatter)


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Start command handler."""
#     if update.effective_user is None:
#         logger.warning("User is None, skipping /start command.")
#         return
#     if update.effective_chat is None:
#         logger.warning("Chat is None, skipping /start command.")
#         return
#     logger.debug(f"User {update.effective_user.id} called /start")
#     session_maker = db.Session
#     async with session_maker() as session:
#         database = db.Database(session=session, user_repo=True)
#         is_user_exists = await database.user.get(update.effective_user.id)
#         print(is_user_exists, type(is_user_exists))
#         if is_user_exists is None:
#             logger.info(f"User <id={update.effective_user.id}> not found, creating...")
#             await database.user.create(
#                 update.effective_user.id,
#                 update.effective_user.username,
#                 update.effective_user.first_name,
#                 update.effective_user.last_name,
#             )
#             logger.info(f"User <id={update.effective_user.id}> was created successfully.")
#         await session.commit()
#     await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello World!")
#     logger.debug(f"User <id={update.effective_user.id}> was greeted.")


def main() -> None:
    """Run bot."""
    application = ApplicationBuilder().token(config("BOT_TOKEN", cast=str)).build()
    logger.debug("Application was built successfully.")
    handlers.add_all_handlers(application)
    logger.debug("All handlers were added successfully.")
    application.run_polling()


if __name__ == "__main__":
    main()
