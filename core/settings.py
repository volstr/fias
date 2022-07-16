import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator

from core.base_settings import BaseSettings


class Settings(BaseSettings):
    class Database(BaseModel):
        class DriverName(str, Enum):
            sqlite = 'sqlite'
            postgresql = 'postgresql'
            mysql = 'mysql'

        driver_name: DriverName = 'sqlite'
        host: Optional[str]
        base: Optional[str]
        user: Optional[str]
        password: Optional[str]
        port: Optional[int]

    class Update(BaseModel):
        class Level(str, Enum):
            street = 'street'
            home = 'home'
            apartment = 'apartment'

        class Hierarchy(str, Enum):
            all = 'all'
            administration = 'administration'
            municipal = 'municipal'

        check: bool = True
        url: str = 'https://fias.nalog.ru/WebServices/Public/GetAllDownloadFileInfo'
        time: str = '00:00'
        level: Level = Level.apartment
        hierarchy: Hierarchy = Hierarchy.all
        region: Optional[int] = None

        @classmethod
        @validator('time')
        def check_time(cls, v):
            try:
                datetime.datetime.strptime(v, '%H:%M')
                return v
            except (TypeError, Exception):
                return '00:00'

    database = Database()
    update = Update()


settings = Settings()
