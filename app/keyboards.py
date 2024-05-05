from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from app.handlers.config import Callbacks


def ADMIN_DECISION_KEYBOARD(application_id: int) -> InlineKeyboardMarkup:  # noqa: N802
    """
    Create an admin keyboard with "Accept" and "Decline" buttons.

    Args:
        application_id (int): Application ID.

    Returns:
        InlineKeyboardMarkup: Keyboard with "Accept" and "Decline" buttons.
        Callback data contains application_id.
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Принять",
                    callback_data=Callbacks.APPLICATION_ACCEPT.value.format(
                        application_id=application_id,
                    ),
                ),
                InlineKeyboardButton(
                    "Отклонить",
                    callback_data=Callbacks.APPLICATION_DECLINE.value.format(
                        application_id=application_id,
                    ),
                ),
            ],
        ],
    )


def ADMIN_HANDLE_APPLICATION_KEYBOARD(application_id: int) -> InlineKeyboardMarkup:  # noqa: N802
    """
    Create a keyboard with "Take in processing" button.

    Args:
        application_id (int): Application ID.

    Returns:
        InlineKeyboardMarkup: Keyboard with "Take in processing" button.
        Callback data contains application_id.

    """
    return InlineKeyboardMarkup(
        (
            (
                InlineKeyboardButton(
                    "Взять в обработку",
                    callback_data=Callbacks.APPLICATION_HANDLE.value.format(
                        application_id=application_id,
                    ),
                ),
            ),
        ),
    )


def ADMIN_DECLINE_KEYBOARD(application_id: int) -> InlineKeyboardMarkup:  # noqa: N802
    """
    Create a keyboard with "Decline" buttons.

    Args:
        application_id (int): Application ID.

    Returns:
        InlineKeyboardMarkup: Keyboard with "Decline" buttons.
        Callback data contains application_id.
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Назад",
                    callback_data=Callbacks.APPLICATION_DECLINE_BACK.value,
                ),
            ],
            [
                InlineKeyboardButton(
                    "Отказать без причины",
                    callback_data=Callbacks.APPLICATION_DECLINE_WITHOUT_REASON.value.format(
                        application_id=application_id,
                    ),
                ),
            ],
        ],
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

REMOVE_INLINE_KEYBOARD = InlineKeyboardMarkup([])
