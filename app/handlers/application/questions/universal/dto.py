from pydantic import BaseModel
from telegram import ReplyKeyboardMarkup
from telegram.ext import ExtBot

from app.config.states import ApplicationStates


class QuestionResponseDTO(BaseModel):
    """DTO for question response."""

    bot: ExtBot
    user_id: int
    message_text: str
    question_number: int
    next_question_text: str | None = None
    next_state: ApplicationStates | None = None
    reply_markup: ReplyKeyboardMarkup | None = None
