from config import ApplicationStates
from handlers.application import about
from handlers.application import activity
from handlers.application import game_mode
from handlers.application import old
from handlers.application import pubg_id
from handlers.application import user_decision
from handlers.start import start_command
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import filters
from telegram.ext import MessageHandler


def add_all_handlers(application: Application):
    """Register all handlers."""
    conv_hander = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            ApplicationStates.pubgID_state: [MessageHandler(filters.ALL, pubg_id)],
            ApplicationStates.old_state: [MessageHandler(filters.ALL, old)],
            ApplicationStates.game_modes_state: [MessageHandler(filters.ALL, game_mode)],
            ApplicationStates.activity_state: [MessageHandler(filters.ALL, activity)],
            ApplicationStates.about_state: [MessageHandler(filters.ALL, about)],
            ApplicationStates.change_or_accept_state: [MessageHandler(filters.ALL, user_decision)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_hander)
