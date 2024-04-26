import datetime as dt
from datetime import datetime, timedelta

from db import UnitOfWork
from loguru import logger
from services.user_service import UserService


class ApplicationService:
    async def is_user_available_to_fill_application(
        self,
        uow: UnitOfWork,
        user_id: int,
    ) -> bool:
        user_service = UserService()
        async with uow:
            result = await user_service.is_user_banned(uow, user_id)
            if result:
                logger.debug(
                    f"Пользователь {user_id=} забанен, FSM заполнения анкеты не запускается",
                )
                return False
            application = await uow.application.retrieve_user_applications(user_id)
            if not application:
                await uow.application.create(user_id)
                return True
            if application.status_id == 1:
                logger.debug(
                    f"Пользователь user_id={application.user_id} заново заполняет анкету",
                )
                await uow.application_answer.delete_all_answers_by_application_id(
                    application.id,
                )
                return True
            if application.status_id == 2:
                logger.debug(
                    f"Заявка пользователя application_id={application.user_id} на рассмотрении, FSM заполнения анкеты не запускается",
                )
                # await chat.send_message(
                #     "Ваша заявка на рассмотрении",
                #     reply_markup=keyboards.REMOVE_KEYBOARD,
                # )
                return False
            if application.status_id == 3:
                logger.debug(
                    f"Заявка пользователя application_id={application.user_id} уже принята, FSM заполнения анкеты не запускается",
                )
                # await chat.send_message(
                #     "Ваша заявка уже была принята",
                #     reply_markup=keyboards.REMOVE_KEYBOARD,
                # )
                return False
            if application.status_id == 4:
                now = datetime.now(dt.UTC)
                if now - application.decision_date < timedelta(days=30):
                    logger.debug(
                        f"Пользователь user_id={application.user_id} пытается подать заявку повторно, но еще не прошло 30 дней, FSM заполнения анкеты не запускается",
                    )
                    # await chat.send_message(
                    #     f"Подача повторной заявки возможна только раз в месяц.\nВы сможете подать заявку {(timedelta(days=30) + application.decision_date).strftime('%d.%m.%Y %H:%M')} (UTC+0).",
                    #     reply_markup=keyboards.REMOVE_KEYBOARD,
                    # )
                    return False
                logger.debug(
                    f"Пользователь user_id={application.user_id} пытается подать заявку повторно, 30 дней прошло, FSM заполнения анкеты запускается",
                )
                await uow.application.create(user_id)
                await uow.commit()
                return True
            return False
