from config import Callbacks
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


def ADMIN_DECISION_KEYBOARD(application_id: int) -> InlineKeyboardMarkup:  # noqa: N802
    """Создание клавиатуры для администраторов.

    Args:
    ----
        application_id (int): Идентификатор заявки.

    Returns:
    -------
        InlineKeyboardMarkup: Клавиатура с кнопками "Принять" и "Отклонить",
        в callback_data передается application_id.

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
    """Создание клавиатуры для взятия заявки в обработку.

    Args:
    ----
        application_id (int): Идентификатор заявки.

    Returns:
    -------
        InlineKeyboardMarkup: Клавиатура с кнопкой "Взять в обработку",
        в callback_data передается application_id.

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


ADMIN_DECLINE_BACK_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "Назад",
                callback_data=Callbacks.APPLICATION_DECLINE_BACK.value,
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
