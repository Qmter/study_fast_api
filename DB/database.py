from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import URL, create_engine, text
from config import settings


sync_engine = create_engine(
    url=settings.DATABASE_URL_sync
) 

async_engine = create_async_engine(
    url=settings.DATABASE_URL_async
) 


async def get_status():
    async with async_engine.connect() as conn:
        res = conn.execute(text('SELECT * from status'))
        print(f'{res=}')