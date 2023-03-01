from sqlalchemy import Column, Integer, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Config


class TableBase:
    pk = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(self) -> str:
        name: str = self.__name__.lower()
        if name.endswith('y'):
            return name[:-1] + 'ies'
        if any([name.endswith(i) for i in ('s', 'ss', 'sh', 'ch', 'x', 'z')]):
            return name + 'es'
        return name + 's'

    @classmethod
    async def create(cls, pk, **kwargs):
        user = cls(pk=pk, **kwargs)  # noqa
        db.add(user)
        await cls.commit()
        return user

    @classmethod
    async def get(cls, pk):
        query = select(cls).where(cls.pk == pk)
        users = await db.execute(query)
        user, = users.first() or None,
        return user

    @classmethod
    async def update(cls, pk, **kwargs):
        query = (
            update(cls)
            .where(cls.pk == pk)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def delete(cls, pk):
        query = delete(cls).where(cls.pk == pk)
        await db.execute(query)
        await cls.commit()
        return True

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
        self._session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()  # noqa

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


db = AsyncDatabaseSession()
