from dataclasses import dataclass


@dataclass
class UserCreateDTO:
    """DTO for user creation."""

    id: int
    username: str | None
    first_name: str | None
    last_name: str | None
