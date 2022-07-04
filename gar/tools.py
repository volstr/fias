import asyncio
from typing import Union, Optional, List, Dict, Type

from fastapi import HTTPException
from starlette import status

from core.async_obj import AsyncObj
from gar.models import AddressObject, House, Apartment, AdministrationHierarchy, MunHierarchy, AddressObjectParam


AddressType = Union[AddressObject, House, Apartment]


async def get_address_object(**_filter) -> Optional[AddressType]:
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

    async def __ainit__(self, model: HierarchyModel, object_id_or_guid: Union[int, str]) -> None:
        obj = await self._get_object(object_id_or_guid)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        self.model: Hierarchy.HierarchyModel = model
        self.object_id: int = obj.object_id

        obj = await self.get_hierarchy_object(self.object_id)
        self.hierarchy = [obj]
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
        self.params: List[AddressObjectParam] = r.pop(-1) if hasattr(r, 'pop') else []
        self.objects: List[Union[AddressType, AddressObjectParam]] = []
        _ = [self.objects.extend(x) for x in r]

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

    @staticmethod
    async def _get_object(object_id_or_guid: Union[int, str]) -> Optional[AddressType]:
        obj: Optional[AddressType] = None
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

    # async def find_child(self, text: str):
    #     _l: List[Hierarchy.HierarchyModel] = await self.model.objects.filter(
    #         object_id=self.object_id
    #     ).order_by(['-is_active', '-start_date']).limit(1).all()

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
        r.update({
            'region_code': self.region_code,
            'kladr': self.kladr,
            'text': f'{", ".join(map(lambda x: x["text"], object_list))}',
        })
        return r
