from app.db.engine import UnitOfWork


class ApplicationRevokeLinkService:
    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize the service instance."""
        self._uow = uow

    async def execute(self, user_id: int):
        """Execute the service."""
        async with self._uow():
            application = await self._uow.application.retrieve_last(user_id)
