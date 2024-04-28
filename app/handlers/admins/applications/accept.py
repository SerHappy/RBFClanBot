from core.config import settings
from decorators import updates
from loguru import logger
from telegram import CallbackQuery, Chat, ChatInviteLink
from telegram.ext import ContextTypes, ExtBot

from app.db.engine import UnitOfWork
from app.domain.admin_processing_application.exceptions import (
    ApplicationAlreadyProcessedError,
    WrongAdminError,
)
from app.domain.application.exceptions import ApplicationWrongStatusError
from app.services.applications.application_admin_accept import (
    ApplicationAdminAcceptService,
)
from app.services.applications.application_formatting import (
    ApplicationFormattingService,
)


@updates.check_update_and_provide_data(need_callback=True)
async def accept_application(
    callback: CallbackQuery,
    chat: Chat,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Обработчик коллбека принятия заявки."""
    if not callback.data:
        logger.error(
            "Получен некорректный callback при попытке вызова accept_application.",
        )
        return
    application_id = int(callback.data.split(":")[-1])
    logger.info(f"Принятие заявки application_id={application_id}.")
    admin_id = callback.from_user.id
    link = await _generate_invite_link(context.application.bot)
    uow = UnitOfWork()
    accept_service = ApplicationAdminAcceptService(uow)
    try:
        application = await accept_service.execute(admin_id, application_id, link)
    except ApplicationAlreadyProcessedError:
        await callback.answer(
            text="Данная заявка уже принята!",
            show_alert=True,
        )
        return
    except WrongAdminError:
        await callback.answer(
            "Вы не можете принять данную заявку.",
            show_alert=True,
        )
        return
    except ApplicationWrongStatusError:
        await callback.answer(
            "Неверный статус заявки.",
            show_alert=True,
        )
        return
    await callback.answer()
    formatting_service = ApplicationFormattingService(uow)
    formatted_application = await formatting_service.execute(application_id)
    await context.bot.edit_message_text(
        chat_id=chat.id,
        message_id=callback.message.message_id,  # type: ignore[reportOptionalMemberAccess]
        text=formatted_application,
        parse_mode="MarkdownV2",
    )
    await context.application.bot.edit_message_text(
        text=formatted_application,
        chat_id=settings.ADMIN_CHAT_ID,
        message_id=context.user_data["application_message_id"],  # type: ignore[reportOptionalSubscript]
        parse_mode="MarkdownV2",
    )
    await chat.send_message(f"Заявка №{application_id} принята.")
    logger.debug(
        (
            f"Заявка application_id={application_id} принята, "
            "уведомляем пользователя и отправляем инвайт"
        ),
    )
    await context.bot.send_message(
        chat_id=application.user_id,
        text=(
            f"Ваша заявка принята!\n"
            f"Ваша персональная ссылка: {application.invite_link}"
        ),
    )
    await context.bot.send_message(
        chat_id=application.user_id,
        text=(
            "Если у вас есть какие-то вопросы или предложения по улучшению, "
            "напишите @RBFManager"
        ),
    )


async def _generate_invite_link(bot: ExtBot) -> str:
    """Генерирует и возвращает ссылку на приглашение.

    Args:
    ----
        bot: Объект Bot.

    Returns:
    -------
        Ссылка на приглашение.

    """
    logger.debug("In generate invite link handler.")
    chat_id = settings.CLAN_CHAT_ID
    link: ChatInviteLink = await bot.create_chat_invite_link(chat_id, member_limit=1)
    return link.invite_link
