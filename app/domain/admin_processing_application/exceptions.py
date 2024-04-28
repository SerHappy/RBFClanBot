class BaseAdminProcessingApplicationError(Exception):
    """Base admin processing application exception."""


class ApplicationAlreadyProcessedError(BaseAdminProcessingApplicationError):
    """Exception raised when application is already processed by an admin."""


class AdminAlreadyProcessedApplicationError(BaseAdminProcessingApplicationError):
    """Exception raised when admin is already processed application."""


class WrongAdminError(BaseAdminProcessingApplicationError):
    """Exception raised when admin is already processed application."""
