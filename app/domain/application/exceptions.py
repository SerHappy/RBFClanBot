from datetime import datetime


class BaseApplicationError(Exception):
    """Base exception for the application domain."""


class ChangeApplicationStatusError(BaseApplicationError):
    """Exception for changing the application status."""


class ApplicationDoesNotExistError(BaseApplicationError):
    """Exception for when an application does not exist."""


class ApplicationAnswerDoesNotExistError(BaseApplicationError):
    """Exception for when an answer does not exist."""


class ApplicationAnswerAlreadyExistError(BaseApplicationError):
    """Exception for when an answer already exists."""


class ApplicationDoesNotCompeteError(BaseApplicationError):
    """Exception for when an application does not complete."""


class ApplicationAlreadyCompleteError(BaseApplicationError):
    """Exception for when an application is already complete."""


class ApplicationAlreadyExistsError(BaseApplicationError):
    """Exception for when an application already exists."""


class ApplicationAtWaitingStatusError(BaseApplicationError):
    """Exception for when an application is in 'WAITING' status."""


class ApplicationAlreadyAcceptedError(BaseApplicationError):
    """Exception for when an application is already accepted."""


class ApplicationDecisionDateNotFoundError(BaseApplicationError):
    """Exception for when an application decision date is not found."""


class ApplicationWrongStatusError(BaseApplicationError):
    """Exception for when an application status is wrong."""


class ApplicationCoolDownError(BaseApplicationError):
    """Exception for when an application is cool down."""

    def __init__(self, cooldown_ends: datetime) -> None:
        """Initialize the application cool down error instance."""
        self.cooldown_ends = cooldown_ends
