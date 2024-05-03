from app.domain.application.entities import Application
from app.domain.application.dto import ApplicationDTO
from app.domain.application.value_objects import ApplicationStatusEnum


def test_create_ok() -> None:
    application = Application(
        data=ApplicationDTO(
            id=1,
            user_id=1,
            status=ApplicationStatusEnum.IN_PROGRESS,
        )
    )

    assert application.id == 1
    assert application.user_id == 1
    assert application.status == ApplicationStatusEnum.IN_PROGRESS
    assert application.decision_date is None
    assert application.invite_link is None
    assert application.rejection_reason is None
    assert application.answers == {}
