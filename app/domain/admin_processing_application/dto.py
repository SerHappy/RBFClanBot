from dataclasses import dataclass


@dataclass
class AdminProcessingApplicationDTO:
    """Data transfer object for an application being processed by an admin."""

    admin_id: int
    application_id: int
