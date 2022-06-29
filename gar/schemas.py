import datetime

from pydantic import BaseModel, validator


class LevelSchema(BaseModel):
    id: int
    name: str
    update_date: datetime.date
    start_date: datetime.date
    end_date: datetime.date
    is_active: bool


class DirectorySchema(BaseModel):
    id: int
    name: str
    short_name: str
    # description: str

    update_date: datetime.date
    start_date: datetime.date
    end_date: datetime.date
    is_active: bool


class ParamTypeSchema(BaseModel):
    id: int
    name: str
    description: str
    code: str

    update_date: datetime.date
    start_date: datetime.date
    end_date: datetime.date
    is_active: bool


class AddressTypeSchema(BaseModel):
    id: int
    name: str
    short_name: str
    level_id: int
    level_name: str
    is_active: bool

    def __init__(self, **kwargs):
        kwargs['level_name'] = kwargs.get('level_id__name')
        super().__init__(**kwargs)


class UpdatesSchema(BaseModel):
    id: int
    update_date: str
    state: str

    def __init__(self, **kwargs):
        if isinstance(kwargs.get('update_date'), datetime.datetime):
            print(kwargs['update_date'].isoformat())
            kwargs['update_date'] = kwargs['update_date'].isoformat()
        super().__init__(**kwargs)
