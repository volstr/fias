import datetime
from typing import Union, Dict, Optional

import ormar

from core.database import BaseMeta


# class Item(ormar.Model):
#     class Meta(BaseMeta):
#         pass
#
#     id: int = ormar.Integer(primary_key=True, comment='Идентификатор')
#     name: str = ormar.String(max_length=100, comment='Какое-то имя поля')
#     # category: Optional[Category] = ormar.ForeignKey(Category, nullable=True)
#
#
# class MyOrders(ormar.Model):
#     class Meta(BaseMeta):
#         tablename = 'my_orders'
#
#     id: int = ormar.Integer(primary_key=True)
#     name: str = ormar.String(max_length=100)
#
#
# class MyOrders2(ormar.Model):
#     class Meta(BaseMeta):
#         tablename = 'my_orders_2'
#
#     id: int = ormar.Integer(primary_key=True)
#     name: str = ormar.String(max_length=100)


# ----------
# alembic init migrations
# alembic revision --autogenerate -m "First"
# alembic upgrade head


class DateModelMixin:
    update_date: datetime.date = ormar.Date(comment='Дата внесения (обновления) записи')
    start_date: datetime.date = ormar.Date(comment='Начало действия записи')
    end_date: datetime.date = ormar.Date(comment='Окончание действия записи')
    is_active: bool = ormar.Boolean(comment='Статус активности')


class Level(ormar.Model, DateModelMixin):
    """
    Сведения по уровням адресных объектов
    """
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True, autoincrement=False, comment='id')
    name: str = ormar.String(max_length=250, index=True, comment='Наименование')
    short_name: str = ormar.String(max_length=50, comment='Краткое наименование')

    def __str__(self):
        return f'{self.id}: {self.name}'


class ParamType(ormar.Model, DateModelMixin):
    """
    Сведения по типу параметра
    """
    class Meta(BaseMeta):
        tablename = 'param_types'

    id: int = ormar.Integer(primary_key=True, autoincrement=False, comment='id')
    name: str = ormar.String(max_length=50, index=True, comment='Наименование')
    code: str = ormar.String(max_length=50, comment='Кодовое обозначение')
    description: str = ormar.String(max_length=120, comment='Описание')

    def __str__(self):
        return f'{self.id}: {self.name}'


class AddressType(ormar.Model, DateModelMixin):
    """
    Сведения по типам адресных объектов
    """
    class Meta(BaseMeta):
        tablename = 'address_types'

    id: int = ormar.Integer(primary_key=True, autoincrement=False, comment='id')
    level_id: Union[Level, Dict] = ormar.ForeignKey(Level, nullable=False,
                                                    comment='Уровень адресного объекта {levels.id}')
    name: str = ormar.String(max_length=250, index=True, comment='Полное наименование типа объекта')
    short_name: str = ormar.String(max_length=50, comment='Краткое наименование типа объекта')
    description: str = ormar.String(max_length=250, nullable=True, comment='Описание')

    def __str__(self):
        return f'{self.id}: {self.name}'


class AddressObject(ormar.Model, DateModelMixin):
    """
    Сведения классификатора адресообразующих элементов
    """
    class Meta(BaseMeta):
        tablename = 'address_objects'

    id: int = ormar.BigInteger(primary_key=True, autoincrement=False, comment='id')
    object_id: int = ormar.Integer(index=True, unique=True,
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


class AdministrationHierarchy(ormar.Model, DateModelMixin):
    """
    Сведения по иерархии в административном делении
    """
    class Meta(BaseMeta):
        tablename = 'administration_hierarchy'

    id: int = ormar.BigInteger(primary_key=True, autoincrement=False, comment='id')
    object_id: Union[AddressObject, Dict] = ormar.ForeignKey(
        AddressObject, name='object_id', index=True, unique=True, nullable=False,
        related_name='administration_hierarchy_object',
        comment='Глобальный уникальный идентификатор адресного объекта {address_objects.object_id}'
    )
    parent_object_id: Optional[Union[AddressObject, Dict]] = ormar.ForeignKey(
        AddressObject, name='object_id', index=True,
        related_name='administration_hierarchy_parent_object',
        comment='Идентификатор родительского объекта {address_objects.object_id}'
    )
    region_code: int = ormar.Integer(comment='Код региона')
    area_code: int = ormar.Integer(comment='Код района')
    city_code: int = ormar.Integer(comment='Код города')
    place_code: int = ormar.Integer(comment='Код населенного пункта')
    plan_code: int = ormar.Integer(comment='Код ЭПС')
    street_code: int = ormar.Integer(comment='Код улицы')

    def __str__(self):
        return f'id: {self.id} object_id: {self.object_id} parent_object_id: {self.parent_object_id}'
