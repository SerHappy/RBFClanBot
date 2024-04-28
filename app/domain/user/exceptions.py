class BaseUserError(Exception):
    """Base exception for the user domain."""


class UserIsBannedError(BaseUserError):
    """Exception for when a user is banned."""

class UserIsNotBannedError(BaseUserError):
    """Exception for when a user is not banned."""

class UserAlreadyExistsError(BaseUserError):
    """Exception for when a user already exists."""


class UserNotFoundError(BaseUserError):
    """Exception for when a user is not found."""
