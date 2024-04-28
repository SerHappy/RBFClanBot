from app.domain.admin_processing_application.dto import AdminProcessingApplicationDTO


class AdminProcessingApplication:
    """Represents an application being processed by an admin."""

    def __init__(self, data: AdminProcessingApplicationDTO) -> None:
        """Initialize the admin processing application instance."""
        self.application_id = data.application_id
        self.admin_id = data.admin_id
