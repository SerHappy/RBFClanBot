import pytest

from app.domain.user.entities import User
from app.domain.user.exceptions import UserIsNotBannedError


@pytest.mark.parametrize(
    "user",
    [
        pytest.param(
            {"is_banned": True},
            marks=pytest.mark.usefixtures("user"),
            id="banned",
        ),
    ],
    indirect=True,
)
def test_ok(user: User) -> None:
    user.unban()
    assert user.is_banned is False


def test_not_banned_fail(user: User) -> None:
    with pytest.raises(UserIsNotBannedError):
        user.unban()
