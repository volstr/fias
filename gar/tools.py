import asyncio
from typing import Union, Optional, List, Dict, Type

from core.async_obj import AsyncObj
from core.database import database
from core.settings import settings
from gar.models import AddressObject, House, Apartment, AdministrationHierarchy, MunHierarchy, AddressObjectParam
from gar.query import sql_find_child

AnyAddressObjectType = Union[AddressObject, House, Apartment]


async def get_address_object(**_filter) -> Optional[AnyAddressObjectType]:
    """
    Получить адресный объект
    """
    tasks = [
        AddressObject.objects.filter(**_filter).select_all().all(),
        House.objects.filter(**_filter).select_all().all(),
        Apartment.objects.filter(**_filter).select_all().all(),
    ]
    for i in await asyncio.gather(*tasks):
        if i and isinstance(i, list):
            return i[0]
    return None


class Hierarchy(AsyncObj):
    HierarchyModel = Union[Type[AdministrationHierarchy], Type[MunHierarchy]]

    def __init__(self, *args, **kwargs):
        self.find_text: Optional[str] = None
        self.found: List[AnyAddressObjectType] = []

        super().__init__(*args, **kwargs)

    async def __ainit__(self, model: HierarchyModel, object_id_or_guid: Union[int, str]) -> None:
        obj = await self._get_object(object_id_or_guid)

        self.model: Hierarchy.HierarchyModel = model
        self.object_id: int = obj.object_id if obj else None

        obj = await self.get_hierarchy_object(self.object_id)
        self.hierarchy = [obj] if obj else []
        while obj and obj.parent_object_id:
            obj = await self.get_hierarchy_object(obj.parent_object_id)
            if obj:
                self.hierarchy.insert(0, obj)

        hierarchy_list = [x.object_id for x in self.hierarchy]

        tasks = [
            AddressObject.objects.filter(object_id__in=hierarchy_list).select_all().all(),
            House.objects.filter(object_id__in=hierarchy_list).select_all().all(),
            Apartment.objects.filter(object_id__in=hierarchy_list).select_all().all(),
            AddressObjectParam.objects.filter(object_id__in=hierarchy_list).all(),
        ]

        r = await asyncio.gather(*tasks)
        self.params: List[AddressObjectParam] = r.pop(-1) if hasattr(r, 'pop') else r[:-1]
        self.objects: List[Union[AnyAddressObjectType, AddressObjectParam]] = []

        # Оставляем тот же порядок, что и при чтении иерархии
        for object_id in hierarchy_list:
            for table in r:
                _ = [self.objects.append(obj) for obj in table if obj.object_id == object_id]

        # Выбираем имя региона
        region_names: List[str] = [x.value for x in self.params if x.param_type_id.id == 16]
        self.region_name: str = region_names[0] if region_names else None
        region_codes: List[int] = [x.region_code for x in self.hierarchy if hasattr(x, 'region_code') and x.region_code]
        self.region_code = region_codes[0] if region_codes else None
        # Выбираем КЛАДР коды
        self.kladrs: List[AddressObjectParam] = [x for x in self.params if x.param_type_id.id == 11]
        self.kladr: Optional[str] = None

        for idx, i in enumerate(self.objects):
            _kladr: List[str] = [x.value for x in self.kladrs if x.object_id == i.object_id]
            self.kladr = _kladr[0] if _kladr else self.kladr

        # Если регион не нашли (муниципальная иерархия) - пытаемся получить его из КЛАДР
        if self.region_code is None and self.kladr:
            self.region_code = int(self.kladr[:2])

    async def find(self, text: str = '', limit: int = 5) -> Optional[AnyAddressObjectType]:
        self.find_text = text

        if settings.database.driver_name == settings.Database.DriverName.sqlite:
            await database.execute("PRAGMA case_sensitive_like=OFF;")

        split_text: List[str] = text.split(';')
        add_num1: Optional[str] = split_text[1] if len(split_text) > 1 else None
        add_num2: Optional[str] = split_text[2] if len(split_text) > 2 else None
        if len(split_text) > 1:
            text = split_text[0]

        params = {
            'object_id': self.object_id,
            'text': f'{text}%',
            'add_num1': add_num1,
            'add_num2': add_num2,
            'limit': limit,
        }
        objects = await database.fetch_all(sql_find_child.format(hierarchy_table=self.model.Meta.tablename), params)
    
        address_objects: List[int] = [x['address_objects'] for x in objects if x['address_objects']]
        houses: List[int] = [x['houses'] for x in objects if x['houses']]
        apartments: List[int] = [x['apartments'] for x in objects if x['apartments']]

        self.found = []
        if address_objects:
            self.found = await AddressObject.objects.filter(object_id__in=address_objects).select_all().all()
        elif houses:
            self.found = await House.objects.filter(object_id__in=houses).select_all().all()
        elif apartments:
            self.found = await Apartment.objects.filter(object_id__in=apartments).select_all().all()

        return self.found

    @staticmethod
    async def _get_object(object_id_or_guid: Union[int, str]) -> Optional[AnyAddressObjectType]:
        obj: Optional[AnyAddressObjectType] = None
        if isinstance(object_id_or_guid, int):
            obj = await get_address_object(object_id=object_id_or_guid)
        elif isinstance(object_id_or_guid, str):
            obj = await get_address_object(object_guid=object_id_or_guid)
        return obj

    async def get_hierarchy_object(self, object_id: int) -> Optional[HierarchyModel]:
        if not object_id:
            return None
        _l = await self.model.objects.filter(object_id=object_id).order_by(['-is_active', '-start_date']).limit(1).all()
        return _l[0] if _l else None

    def dict(self, objects: bool = False, hierarchy: bool = False) -> Dict:
        object_list: List[Dict] = []
        for i in self.objects:
            kladr_list = [x.value for x in self.kladrs if x.object_id == i.object_id]
            obj: dict = i.dict()
            obj['kladr'] = kladr_list[0] if kladr_list else None
            obj['text'] = str(self.region_name) if hasattr(i, 'level_id') and i.level_id.id == 1 and self.region_name \
                else str(i)
            object_list.append(obj)

        r = {}
        if objects:
            r['objects'] = object_list
        if hierarchy:
            r['hierarchy'] = self.hierarchy
        if self.find_text is not None:
            r['found'] = self.found

        r.update({
            'region_code': self.region_code,
            'kladr': self.kladr,
            'text': f'{", ".join(map(lambda x: x["text"], object_list))}',
        })
        return r
