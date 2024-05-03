import pytest


from app.domain.user.dto import UserDTO
from app.domain.user.entities import User
from app.domain.user.exceptions import UserIsBannedError, UserIsNotBannedError


def test_create_without_specifying_is_banned_ok() -> None:
    entity = User(
        data=UserDTO(
            id=1,
            username="@username",
            first_name="name",
            last_name="lastname",
        ),
    )
    assert entity.id == 1
    assert entity.username == "@username"
    assert entity.first_name == "name"
    assert entity.last_name == "lastname"
    assert entity.is_banned is False


def test_create_wit_specifying_is_banned_ok() -> None:
    entity = User(
        data=UserDTO(
            id=1,
            username="@username",
            first_name="name",
            last_name="lastname",
            is_banned=True,
        ),
    )
    assert entity.id == 1
    assert entity.username == "@username"
    assert entity.first_name == "name"
    assert entity.last_name == "lastname"
    assert entity.is_banned is True
