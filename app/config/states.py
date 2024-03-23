from enum import Enum


class ApplicationStates(Enum):
    """Application states."""

    pubgID_state = 1
    old_state = 2
    game_modes_state = 3
    activity_state = 4
    about_state = 5
    change_or_accept_state = 6


class DeclineUserStates(Enum):
    """Decline user states."""

    decline_reason_state = 1
