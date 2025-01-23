import asyncpg

class Database:
    pool = None

    @classmethod
    async def connect(cls, dsn: str):
        cls.pool = await asyncpg.create_pool(dsn=dsn)

    @classmethod
    async def disconnect(cls):
        if cls.pool:
            await cls.pool.close()
            cls.pool = None