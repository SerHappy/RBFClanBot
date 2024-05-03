import pytest


from app.domain.user.entities import User
from app.domain.user.exceptions import UserIsBannedError


def test_ok(user: User) -> None:
    user.ban()
    assert user.is_banned is True


@pytest.mark.parametrize(
    "user",
    [
        pytest.param(
            {"is_banned": True},
            marks=pytest.mark.usefixtures("user"),
            id="banned",
        )
    ],
    indirect=True,
)
def test_already_banned_fail(user: User) -> None:
    with pytest.raises(UserIsBannedError):
        user.ban()
