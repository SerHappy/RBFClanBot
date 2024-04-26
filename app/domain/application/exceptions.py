class BaseApplicationError(Exception):
    """Base exception for the application domain."""


class ChangeApplicationStatusError(BaseApplicationError):
    """Exception for changing the application status."""


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
