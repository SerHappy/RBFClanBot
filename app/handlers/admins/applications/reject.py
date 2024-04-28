from datetime import timedelta

import keyboards
from config import DeclineUserStates
from core.config import settings
from decorators import updates
from loguru import logger
from telegram import CallbackQuery, Chat, Message
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler

from app.db.engine import UnitOfWork
from app.domain.admin_processing_application.exceptions import (
    ApplicationAlreadyProcessedError,
    WrongAdminError,
)
from app.domain.application.exceptions import ApplicationWrongStatusError
from app.services.applications.application_admin_reject import (
    ApplicationAdminRejectService,
)
from app.services.applications.application_formatting import (
    ApplicationFormattingService,
)


@updates.check_update_and_provide_data(need_callback=True)
async def reject_application_start(
    callback: CallbackQuery,
    chat: Chat,
    context: CallbackContext,
) -> int:
    """Обработчик коллбека отклонения заявки."""
    if not callback.data:
        logger.error(
            "Получен некорректный callback при попытке вызова accept_application.",
        )
        return ConversationHandler.END
    await callback.answer()
    context.user_data["message"] = callback.message  # type: ignore[reportOptionalSubscript]
    logger.debug(f"Сохранение переменной message={callback.message}.")
    application_id = int(callback.data.split(":")[-1])
    logger.info(f"Отклонение заявки application_id={application_id}.")
    context.user_data["application_id"] = application_id  # type: ignore[reportOptionalSubscript]
    logger.debug(f"Сохранение переменной application_id={application_id}.")
    await callback.edit_message_reply_markup(keyboards.ADMIN_DECLINE_BACK_KEYBOARD)
    logger.debug("Клавиатура обновлена.")
    await chat.send_message(
        f"Напишите причину отказа для Заявки №{application_id}",
    )
    return DeclineUserStates.DECLINE_REASON_STATE


@updates.check_update_and_provide_data(need_message=True)
async def reject_reason_hander(
    message: Message,
    chat: Chat,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Обработчик причины отказа."""
    if not message.text:
        logger.error("Получена некорректная причина отказа.")
        return ConversationHandler.END
    application_id = context.user_data["application_id"]  # type: ignore[reportOptionalSubscript]
    admin = message.from_user
    if not admin:
        logger.error(
            "Получен некорректный admin при попытке вызова reject_reason_hander.",
        )
        return ConversationHandler.END
    logger.info(f"Получение причины отказа application_id={application_id}.")
    await chat.send_message(
        f"Причина отказа для Заявки №{application_id}:\n{message.text}.",
    )
    uow = UnitOfWork()
    reject_service = ApplicationAdminRejectService(uow)
    try:
        application = await reject_service.execute(
            admin.id,
            application_id,
            message.text,
        )
    except ApplicationAlreadyProcessedError:
        await chat.send_message(
            text="Данная заявка уже принята!",
        )
        return ConversationHandler.END
    except WrongAdminError:
        await chat.send_message(
            "Вы не можете принять данную заявку.",
        )
        return ConversationHandler.END
    except ApplicationWrongStatusError:
        await chat.send_message(
            "Неверный статус заявки.",
        )
        return ConversationHandler.END
    message_to_update: Message = context.user_data["message"]  # type: ignore[reportOptionalSubscript]
    formatting_service = ApplicationFormattingService(uow)
    formatted_application = await formatting_service.execute(application_id)
    await message_to_update.edit_text(
        text=formatted_application,
        reply_markup=keyboards.REMOVE_INLINE_KEYBOARD,
        parse_mode="MarkdownV2",
    )
    await context.application.bot.edit_message_text(
        formatted_application,
        chat_id=settings.ADMIN_CHAT_ID,
        message_id=context.user_data["application_message_id"],  # type: ignore[reportOptionalSubscript]
        parse_mode="MarkdownV2",
    )
    logger.debug("Текст заявки обновлен.")
    await chat.send_message(f"Заявка №{application_id} отклонена.")
    logger.debug(
        (
            f"Заявка application_id={application_id} отклонена, "
            "уведомляем пользователя и отправляем причину отказа"
        ),
    )
    await context.bot.send_message(
        chat_id=application.user_id,
        text=(
            "Ваша заявка отклонена.\n"
            "Причина отказа: {}.\n"
            "Попробуйте снова {} (UTC+0)."
        ).format(
            application.rejection_reason,
            (timedelta(days=30) + application.decision_date).strftime(  # type: ignore[reportOperatorIssue]
                "%d.%m.%Y %H:%M %Z",
            ),
        ),
    )
    await context.bot.send_message(
        chat_id=application.user_id,
        text=(
            "Если у вас есть какие-то вопросы или предложения по улучшению, "
            "напишите @RBFManager"
        ),
    )
    return ConversationHandler.END


@updates.check_update_and_provide_data(need_callback=True)
async def reject_back_button_handler(
    callback: CallbackQuery,
    chat: Chat,  # noqa: ARG001
    context: CallbackContext,
) -> int:
    """Обработчик кнопки Назад в чате админов."""
    await callback.answer()
    logger.debug("In decline back handler.")
    logger.info("Возврат к выбору действий для Заявки.")
    application_id = context.user_data["application_id"]  # type: ignore[reportOptionalSubscript]
    logger.debug(f"Возврат к выбору действий для Заявки №{application_id}")
    await callback.edit_message_reply_markup(
        keyboards.ADMIN_DECISION_KEYBOARD(application_id),
    )
    return ConversationHandler.END
