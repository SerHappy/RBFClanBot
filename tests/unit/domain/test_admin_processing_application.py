from app.domain.admin_processing_application.entities import AdminProcessingApplication
from app.domain.admin_processing_application.dto import AdminProcessingApplicationDTO


def test_create_ok() -> None:
    entity = AdminProcessingApplication(
        data=AdminProcessingApplicationDTO(
            admin_id=1,
            application_id=1,
        )
    )
    assert entity.admin_id == 1
    assert entity.application_id == 1
