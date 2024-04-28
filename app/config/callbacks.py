from enum import StrEnum


class Callbacks(StrEnum):
    """Callbacks for bot."""

    APPLICATION_ACCEPT = "application_accept:{application_id}"
    APPLICATION_DECLINE = "application_decline:{application_id}"
    APPLICATION_DECLINE_BACK = "back_application_decline"
    APPLICATION_HANDLE = "application_handle:{application_id}"
