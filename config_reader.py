from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from datetime import datetime


class Settings(BaseSettings):
    # Желательно вместо str использовать SecretStr 
    # для конфиденциальных данных, например, токена бота
    bot_token: SecretStr
    app_name: str
    pg_user: str
    pg_pwd: SecretStr
    pg_host: str
    pg_dbname: str
    maezztro_tid: int

    # Начиная со второй версии pydantic, настройки класса настроек задаются
    # через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан
    # с кодировкой UTF-8
    model_config = SettingsConfigDict(env_file='config/.env', env_file_encoding='utf-8')


class Variables:
    # def __init__(self, superuser):
    #     self.superuser = superuser
    superuser: list
    registred_users: list
    doctors: dict
    appointments: dict
    administrator: list
    # picked_date: datetime
    # user_tid: int
    # search_user: dict
    test_var: str


# При импорте файла сразу создастся 
# и провалидируется объект конфига, 
# который можно далее импортировать из разных мест
config = Settings()
myvars = Variables()
DEBUG = 1
