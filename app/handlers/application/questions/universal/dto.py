from pydantic import BaseModel, ConfigDict
from telegram import ReplyKeyboardMarkup
from telegram.ext import ExtBot

from app.config.states import ApplicationStates


class QuestionResponseDTO(BaseModel):
    """DTO for question response."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    bot: ExtBot
    user_id: int
    message_text: str
    question_number: int
    next_question_text: str | None = None
    next_state: ApplicationStates | None = None
    reply_markup: ReplyKeyboardMarkup | None = None
