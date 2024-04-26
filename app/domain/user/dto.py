from dataclasses import dataclass


@dataclass
class UserDTO:
    """Data transfer object for User model."""

    id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    is_banned: bool = False
