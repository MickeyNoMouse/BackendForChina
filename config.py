from pydantic_settings import BaseSettings  # Импорт BaseSettings для создания настроек
from dotenv import load_dotenv  # Импортир функции load_dotenv для загрузки переменных из .env

# Загрузка переменных из файла .env в переменные окружения
load_dotenv()


class Settings(BaseSettings):  # Наследуем от BaseSettings, чтобы автоматически читать переменные среды (в частности данные из .env)
    # Задаем настройки приложения
    app_name: str = "Simple China"
    admin_email: str = "mikhailcherevkov@gmail.com"

    # Настройки для подключения к базе данных PostgreSQL
    POSTGRES_USER: str  # Имя пользователя базы данных, считывается автоматически из .env
    POSTGRES_PASSWORD: str  # Пароль пользователя, считывается автоматически из .env
    POSTGRES_HOST: str  # Хост базы данных, считывается автоматически из .env
    POSTGRES_PORT: int  # Порт для подключения, считывается автоматически из .env
    POSTGRES_DB: str  # Имя базы данных, считывается автоматически из .env

    # Свойство для создания синхронного URL подключения к PostgreSQL
    @property
    def POSTGRES_URLS(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Свойство для создания асинхронного URL подключения к PostgreSQL
    @property
    def POSTGRES_URLA(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# Создаем экземпляр класса Settings, который автоматически считывает переменные из .env
settings = Settings()
