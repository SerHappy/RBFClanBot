from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    """Data transfer object for User model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    is_banned: bool = False
