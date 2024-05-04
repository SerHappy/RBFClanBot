from app.db.engine import UnitOfWork


class TestUnitOfWork(UnitOfWork):
    __test__ = False

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory
