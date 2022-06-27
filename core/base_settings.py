import json
import os
from json import JSONDecodeError

from pydantic import BaseModel


class BaseSettings(BaseModel):
    __instance = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not kwargs:
            self.load()

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @property
    def file_name(self) -> str:
        return os.path.join(os.getcwd(), 'settings.json')

    def load(self) -> bool:
        """
        Прочитать настройки из файла
        """
        try:
            parse = self.parse_file(self.file_name)
            for i in parse.dict():
                value = getattr(parse, i)
                setattr(self, i, value)
            self.save()
        except FileNotFoundError:
            self.save()
        except OSError:
            return False
        except JSONDecodeError:
            return False
        return True

    def save(self) -> bool:
        """
        Сохранить файл настроек
        """
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.dict(), f, indent=4, ensure_ascii=False)
        except Exception as e:
            # log.critical(e)
            raise e
        return True

    def is_sync(self) -> bool:
        """
        Соответствуют ли настройки в файле тому, что загружено в память
        """
        try:
            with open(self.file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                in_file = json.dumps(data, ensure_ascii=False)
                in_settings = json.dumps(self.dict(), ensure_ascii=False)
                return hash(in_file) == hash(in_settings)
        except OSError:
            return False
        except JSONDecodeError:
            return False

    def sync(self) -> bool:
        """
        Проверяем, изменились ли настройки в файле. Если изменились - перезагружаем его
        """
        if not self.is_sync():
            return self.load()
