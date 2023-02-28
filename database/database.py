from sqlalchemy import Integer, Column, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Config


class TableBase:
    pk = Column(Integer, autoincrement=True, primary_key=True)

    @property
    def id(self):
        return self.pk

    @classmethod
    async def commit(cls):
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def get_all(cls):
        query = select(cls)
        users = await db.execute(query)
        users = users.scalars().all()
        return users

    @declared_attr
    def __tablename__(cls) -> str:
        name: str = cls.__name__.lower()
        if name.endswith('y'):
            return name[:-1] + 'ies'
        if any([name.endswith(i) for i in ('s', 'ss', 'sh', 'ch', 'x', 'z')]):
            return name + 'es'
        return name + 's'


Base = declarative_base(cls=TableBase)


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            Config.DB_CONFIG,
            future=True,
            echo=True,
        )
        self._session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


db = AsyncDatabaseSession()
