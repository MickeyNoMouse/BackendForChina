from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # Импортируем классы для создания асинхронной сессии и движка
from sqlalchemy.orm import sessionmaker  # Импортируем sessionmaker для создания фабрики сессий

#from models.models import Base  # Импортируем базовый класс моделей из файла models, где определены все таблицы

from config import settings  # Импортируем настройки подключения к базе данных из config.py


async_engine = create_async_engine(settings.POSTGRES_URLA, echo=True) # Создаем асинхронный движок для работы с базой данных

async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False) # Создаем фабрику сессий для асинхронных запросов к базе данных.

''' 
 async def init_db(): # Асинхронная функция для инициализации базы данных (создания таблиц).
    async with async_engine.begin() as conn: # Открываем асинхронное подключение
        await conn.run_sync(Base.metadata.create_all) # Создаем все таблицы, описанные в models
'''

async def get_db(): # Асинхронный генератор, возвращающий сессию для запросов к базе данных.
    async with async_session() as session:  # Открываем новую асинхронную сессию
        try:
            yield session # Возвращаем сессию как генератор
        finally:
            await session.close() # Закрываем сессию после завершения использования
'''
async def create_async_tables(): # Асинхронная функция для пересоздания таблиц базы данных.
    async with async_engine.begin() as conn: 
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
 
'''
# async def init_db() и async def create_async_tables() не используем при создании и заполнении таблиц бд вручную