from app.domain.user.dto import UserDTO
from app.domain.user.exceptions import UserIsBannedError


class User:
    """Represents a user domain object."""

    def __init__(self, data: UserDTO) -> None:
        """Initialize the user instance."""
        self.id = data.id
        self.username = data.username
        self.first_name = data.first_name
        self.last_name = data.last_name
        self.is_banned = data.is_banned

    def check_is_user_banned(self) -> None:
        """Check if the user is banned.

        Raises
        ------
            UserIsBannedError: If the user is banned.

        """
        if self.is_banned:
            raise UserIsBannedError
