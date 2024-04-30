from enum import IntEnum


class ApplicationStates(IntEnum):
    """Application states."""

    PUBG_ID_STATE = 1
    AGE_STATE = 2
    GAME_MODES_STATE = 3
    ACTIVITY_STATE = 4
    ABOUT_STATE = 5
    CHANGE_OR_ACCEPT_STATE = 6


class DeclineUserStates(IntEnum):
    """Decline user states."""

    DECLINE_REASON_STATE = 1
