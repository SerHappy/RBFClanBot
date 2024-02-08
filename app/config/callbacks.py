from enum import Enum


class Callbacks(Enum):
    """Callbacks for bot."""

    APPLICATION_ACCEPT = "application_accept"
    APPLICATION_DECLINE = "application_decline"
    APPLICATION_DECLINE_BACK = "application_decline_back"
