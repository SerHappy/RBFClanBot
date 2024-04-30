from pydantic import BaseModel, ConfigDict


class AdminProcessingApplicationDTO(BaseModel):
    """Data transfer object for an application being processed by an admin."""

    model_config = ConfigDict(from_attributes=True)

    admin_id: int
    application_id: int
