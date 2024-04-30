from loguru import logger
from telegram import CallbackQuery, Chat
from telegram.ext import ContextTypes, ConversationHandler

from app import keyboards
from app.db.engine import UnitOfWork
from app.decorators import updates
from app.domain.admin_processing_application.exceptions import (
    AdminAlreadyProcessedApplicationError,
    ApplicationAlreadyProcessedError,
)
from app.domain.application.exceptions import ApplicationWrongStatusError
from app.services.applications.application_admin_take import (
    ApplicationAdminTakeService,
)
from app.services.applications.application_formatting import (
    ApplicationFormattingService,
)


# TODO: Переименовать функцию
@updates.check_update_and_provide_data(need_callback=True)
async def take_application_handler(
    callback: CallbackQuery,
    chat: Chat,
    context: ContextTypes.DEFAULT_TYPE,
) -> int | None:
    """Взятие заявки в обработку."""
    callback_data = callback.data
    admin_id = callback.from_user.id
    application_message = callback.message
    if (
        not callback_data
        or not application_message
        or not application_message.is_accessible
    ):
        logger.error(
            (
                "Получен некорректный callback или "
                "message при попытке вызова take_application."
            ),
        )
        return ConversationHandler.END
    application_id = int(callback_data.split(":")[-1])
    logger.info(f"Администратор {admin_id=} взял заявку {application_id=} в обработку.")
    uow = UnitOfWork()
    service = ApplicationAdminTakeService(uow)
    try:
        await service.execute(admin_id, application_id)
    except AdminAlreadyProcessedApplicationError:
        await callback.answer(
            text="Вы уже взяли заявку в обработку!",
            show_alert=True,
        )
        return ConversationHandler.END
    except ApplicationAlreadyProcessedError:
        await callback.answer(
            text="Заявка уже в обработке!",
            show_alert=True,
        )
        return ConversationHandler.END
    except ApplicationWrongStatusError:
        await callback.answer(
            text="Невозможно взять в обработку заявку",
            show_alert=True,
        )
        return ConversationHandler.END

    formatting_service = ApplicationFormattingService(uow)
    formatted_application = await formatting_service.execute(application_id)
    await context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=application_message.message_id,
        text=formatted_application,
        parse_mode="MarkdownV2",
    )
    await context.application.bot.send_message(
        chat_id=admin_id,
        text=formatted_application,
        reply_markup=keyboards.ADMIN_DECISION_KEYBOARD(application_id),
        parse_mode="MarkdownV2",
    )
    context.user_data["application_message_id"] = application_message.message_id  # type: ignore[reportOptionalSubscript]
    await callback.answer(
        text=(
            "Заявка взята в обработку! "
            "Зайдите в личные сообщения для дальнейшей работы."
        ),
        show_alert=True,
    )
    return None
