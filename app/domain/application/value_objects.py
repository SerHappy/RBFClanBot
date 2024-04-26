from enum import IntEnum, StrEnum


class ApplicationStatusEnum(StrEnum):
    """Status of an application."""

    ACCEPTED = "Принята"
    REJECTED = "Отклонена"
    IN_PROGRESS = "В процессе заполнения"
    WAITING = "Ожидает рассмотрения"
    PROCESSING = "На рассмотрении"


class ApplicationQuestionEnum(IntEnum):
    """Questions for the application."""

    PUBG_ID = 1
    AGE = 2
    GAME_MODES = 3
    GAME_TIME = 4
    ACTIVITY = 5

    @classmethod
    def all_ids(cls: "type[ApplicationQuestionEnum]") -> tuple:
        """Return all question ids."""
        return tuple(question.value for question in cls)
