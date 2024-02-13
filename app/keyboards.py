from config import Callbacks
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove


ADMIN_DECISION_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Принять", callback_data=Callbacks.APPLICATION_ACCEPT.value),
            InlineKeyboardButton("Отклонить", callback_data=Callbacks.APPLICATION_DECLINE.value),
        ],
    ]
)
ADMIN_DECLINE_BACK_KEYBOARD = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Назад", callback_data=Callbacks.APPLICATION_DECLINE_BACK.value)]]
)

USER_SKIP_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Пропустить")],
    ],
    resize_keyboard=True,
)

USER_DECISION_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton("1"),
            KeyboardButton("2"),
            KeyboardButton("3"),
        ],
        [
            KeyboardButton("4"),
            KeyboardButton("5"),
            KeyboardButton("6"),
        ],
    ],
    resize_keyboard=True,
)

REMOVE_KEYBOARD = ReplyKeyboardRemove()
