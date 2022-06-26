import datetime
from typing import Union, Dict

import ormar

from core.database import BaseMeta


# alembic init migrations
# alembic revision --autogenerate -m "First"
# alembic upgrade head


class DateModelMixin:
    update_date: datetime.date = ormar.Date(comment='Дата внесения (обновления) записи')
    start_date: datetime.date = ormar.Date(comment='Начало действия записи')
    end_date: datetime.date = ormar.Date(comment='Окончание действия записи')
    is_active: bool = ormar.Boolean(comment='Статус активности')


class DirectoryBase(ormar.Model, DateModelMixin):
    """
    Базовый класс справочников типов
    """
    class Meta(BaseMeta):
        abstract = True

    id: int = ormar.Integer(primary_key=True, autoincrement=False, comment='id')
    name: str = ormar.String(max_length=250, index=True, comment='Полное наименование типа объекта')
    short_name: str = ormar.String(max_length=50, nullable=True, comment='Краткое наименование типа объекта')
    description: str = ormar.String(max_length=250, nullable=True, comment='Описание')

    def __str__(self):
        return f'{self.id}: {self.name}'


class Level(ormar.Model, DateModelMixin):
    """
    Сведения по уровням адресных объектов
    """
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True, autoincrement=False, comment='id')
    name: str = ormar.String(max_length=250, index=True, comment='Наименование')
    # short_name: str = ormar.String(max_length=50, nullable=True, comment='Краткое наименование')

    def __str__(self):
        return f'{self.id}: {self.name}'


class ParamType(DirectoryBase):
    """
    Сведения по типу параметра
    """
    class Meta(BaseMeta):
        tablename = 'param_types'

    code: str = ormar.String(max_length=50, comment='Кодовое обозначение')


class AddressType(DirectoryBase):
    """
    Сведения по типам адресных объектов
    """
    class Meta(BaseMeta):
        tablename = 'address_types'

    level_id: Union[Level, Dict] = ormar.ForeignKey(Level, nullable=False,
                                                    comment='Уровень адресного объекта {levels.id}')


class HouseType(DirectoryBase):
    """
    Признаки владения
    """
    class Meta(BaseMeta):
        tablename = 'house_types'


class ApartmentType(DirectoryBase):
    """
    Типы помещений
    """
    class Meta(BaseMeta):
        tablename = 'apartment_type'


class AddressObject(ormar.Model, DateModelMixin):
    """
    Сведения классификатора адресообразующих элементов
    """
    class Meta(BaseMeta):
        tablename = 'address_objects'

    id: int = ormar.BigInteger(primary_key=True, autoincrement=False, comment='id')
    object_id: int = ormar.BigInteger(index=True, unique=True,
                                      comment='Глобальный уникальный идентификатор адресного объекта')
    object_guid: str = ormar.String(
        max_length=36, index=True,
        comment='Глобальный уникальный идентификатор адресного объекта. Соответствует коду ФИАС'
    )
    name: str = ormar.String(max_length=250, index=True, comment='Наименование')
    type_name: str = ormar.String(max_length=50, comment='Краткое наименование типа объекта')
    level_id: Union[Level, Dict] = ormar.ForeignKey(Level, nullable=False,
                                                    comment='Уровень адресного объекта {levels.id}')
    is_actual: bool = ormar.Boolean(comment='Статус актуальности адресного объекта ФИАС')

    def __str__(self):
        return f'id: {self.id} - {self.name}'


class House(ormar.Model, DateModelMixin):
    """
    Сведения по номерам домов улиц городов и населенных пунктов
    """
    class Meta(BaseMeta):
        pass

    id: int = ormar.BigInteger(primary_key=True, autoincrement=False, comment='id')
    object_id: int = ormar.BigInteger(index=True, unique=True,
                                      comment='Глобальный уникальный идентификатор адресного объекта')
    object_guid: str = ormar.String(
        max_length=36, index=True,
        comment='Глобальный уникальный идентификатор адресного объекта. Соответствует коду ФИАС'
    )
    house_num: str = ormar.String(max_length=50, index=True, nullable=True, comment='Основной номер дома')
    add_num1: str = ormar.String(max_length=50, index=True, nullable=True, comment='Дополнительный номер дома 1')
    add_num2: str = ormar.String(max_length=50, index=True, nullable=True, comment='Дополнительный номер дома 2')
    house_type: Union[HouseType, Dict] = ormar.ForeignKey(HouseType, nullable=True, related_name='house_house_type',
                                                          comment='Основной тип дома {house_types.id}')
    add_type1: Union[HouseType, Dict] = ormar.ForeignKey(HouseType, nullable=True, related_name='house_add_type1',
                                                         comment='Дополнительный тип дома 1 {house_types.id}')
    add_type2: Union[HouseType, Dict] = ormar.ForeignKey(HouseType, nullable=True, related_name='house_add_type2',
                                                         comment='Дополнительный тип дома 2 {house_types.id}')
    is_actual: bool = ormar.Boolean(comment='Статус актуальности адресного объекта ФИАС')

    def __str__(self):
        return f'id: {self.id} object_id: {self.object_id}'


class Apartment(ormar.Model, DateModelMixin):
    """
    Сведения по помещениям
    """
    class Meta(BaseMeta):
        pass

    id: int = ormar.BigInteger(primary_key=True, autoincrement=False, comment='id')
    object_id: int = ormar.BigInteger(index=True, unique=True,
                                      comment='Глобальный уникальный идентификатор адресного объекта')
    object_guid: str = ormar.String(
        max_length=36, index=True,
        comment='Глобальный уникальный идентификатор адресного объекта. Соответствует коду ФИАС'
    )
    number: str = ormar.String(max_length=50, index=True, nullable=False, comment='Номер помещения')
    apartment_type_id: Union[ApartmentType, Dict] = ormar.ForeignKey(
        ApartmentType, nullable=False,
        comment='Уровень адресного объекта {apartment_type.id}'
    )
    is_actual: bool = ormar.Boolean(comment='Статус актуальности адресного объекта ФИАС')


class AdministrationHierarchy(ormar.Model, DateModelMixin):
    """
    Сведения по иерархии в административном делении
    """
    class Meta(BaseMeta):
        tablename = 'hierarchy_adm'

    id: int = ormar.BigInteger(primary_key=True, autoincrement=False, comment='id')
    object_id: int = ormar.BigInteger(
        index=True, nullable=False,
        comment='Глобальный уникальный идентификатор адресного объекта '
                '{address_objects | houses | apartments -> object_id}'
    )
    parent_object_id: int = ormar.BigInteger(
        index=True, nullable=True,
        comment='Идентификатор родительского объекта {address_objects | houses | apartments -> object_id}'
    )
    region_code: int = ormar.Integer(nullable=True, comment='Код региона')
    area_code: int = ormar.Integer(nullable=True, comment='Код района')
    city_code: int = ormar.Integer(nullable=True, comment='Код города')
    place_code: int = ormar.Integer(nullable=True, comment='Код населенного пункта')
    plan_code: int = ormar.Integer(nullable=True, comment='Код ЭПС')
    street_code: int = ormar.Integer(nullable=True, comment='Код улицы')

    def __str__(self):
        return f'id: {self.id} object_id: {self.object_id} parent_object_id: {self.parent_object_id}'


class MunHierarchy(ormar.Model, DateModelMixin):
    """
    Сведения по иерархии в административном делении
    """
    class Meta(BaseMeta):
        tablename = 'hierarchy_mun'

    id: int = ormar.BigInteger(primary_key=True, autoincrement=False, comment='id')
    object_id: int = ormar.BigInteger(
        index=True, nullable=False,
        comment='Глобальный уникальный идентификатор адресного объекта '
                '{address_objects | houses | apartments -> object_id}'
    )
    parent_object_id: int = ormar.BigInteger(
        index=True, nullable=True,
        comment='Идентификатор родительского объекта {address_objects | houses | apartments -> object_id}'
    )
    oktmo: str = ormar.String(max_length=50, comment='Код ОКТМО')
    path: str = ormar.String(max_length=250, nullable=True,
                             comment='Материализованный путь к объекту (полная иерархия)')


class AddressObjectParam(ormar.Model):
    """
    Сведения по типу параметра
    """
    class Meta(BaseMeta):
        tablename = 'address_object_params'

    id: int = ormar.BigInteger(primary_key=True, autoincrement=False, comment='id')
    object_id: int = ormar.BigInteger(
        index=True, nullable=False,
        comment='Глобальный уникальный идентификатор адресного объекта '
                '{address_objects | houses | apartments -> object_id}'
    )
    param_type_id: Union[ParamType, Dict] = ormar.ForeignKey(
        ParamType, nullable=False,
        comment='Тип параметра {param_types.id}'
    )
    value: str = ormar.String(max_length=128, nullable=False, index=True, comment='Значение параметра')
    update_date: datetime.date = ormar.Date(comment='Дата внесения (обновления) записи')
    start_date: datetime.date = ormar.Date(comment='Начало действия записи')
    end_date: datetime.date = ormar.Date(comment='Окончание действия записи')

    def __str__(self):
        return self.value
