from app.domain.user.dto import UserDTO
from app.domain.user.exceptions import UserIsBannedError, UserIsNotBannedError


class User:
    """Represents a user domain object."""

    def __init__(self, data: UserDTO) -> None:
        """
        Initialize the user instance.

        Args:
            data (UserDTO): The data of the user.

        Returns:
            None
        """
        self.id = data.id
        self.username = data.username
        self.first_name = data.first_name
        self.last_name = data.last_name
        self.is_banned = data.is_banned

    def ban(self) -> None:
        """Ban the user."""
        if self.is_banned:
            raise UserIsBannedError
        self.is_banned = True

    def unban(self) -> None:
        """Unban the user."""
        if not self.is_banned:
            raise UserIsNotBannedError
        self.is_banned = False

    def check_is_user_banned(self) -> None:
        """Check if the user is banned."""
        if self.is_banned:
            raise UserIsBannedError
