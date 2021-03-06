from typing import List, Optional, Union

from fastapi import APIRouter, HTTPException
from starlette import status

from gar.models import Level, AddressType, ParamType, HouseType, ApartmentType, Updates, AdministrationHierarchy, \
    MunHierarchy, AddressObjectParam
from gar.schemas import LevelSchema, DirectorySchema, ParamTypeSchema, AddressTypeSchema, UpdatesSchema
from gar.tools import get_address_object, Hierarchy

router_types = APIRouter(prefix='/api', tags=['ГАР / ФИАС - Типы объектов'])
router = APIRouter(prefix='/api', tags=['ГАР / ФИАС'])


@router_types.get("/levels", response_model=List[LevelSchema])
async def levels():
    """
    Сведения по уровням адресных объектов
    """
    return await Level.objects.all()


@router_types.get("/house_types", response_model=List[DirectorySchema])
async def house_types():
    """
    Признаки владения
    """
    return await HouseType.objects.all()


@router_types.get("/apartment_types", response_model=List[DirectorySchema])
async def house_types():
    """
    Признаки владения
    """
    return await ApartmentType.objects.all()


@router_types.get("/param_types", response_model=List[ParamTypeSchema])
async def param_types():
    """
    Сведения по типу параметра
    """
    return await ParamType.objects.all()


@router_types.get("/address_types", response_model=List[AddressTypeSchema])
async def address_types(is_active: Optional[Union[bool, int]] = None):
    """
    Сведения по уровням адресных объектов
    """
    obj = AddressType.objects.select_related('level_id')
    if is_active:
        obj = obj.filter(is_active=True)

    fields = 'id', 'name', 'short_name', 'level_id', 'is_active', 'level_id__name'
    return await obj.values(fields)


@router.get("/updates", response_model=List[UpdatesSchema])
async def updates():
    """
    Сведения по уровням адресных объектов
    """
    return await Updates.objects.all()


@router.get("/objects/object/{object_id}")
async def object_by_id(object_id: Union[int, str]):
    """
    <strong>Получить любой адресный объект по object_id или по object_guid</strong>

    К адресным объектам относится все, в том числе населенные пункты, улицы, дома, квартиры
    """
    _filter = {'object_id': object_id} if isinstance(object_id, int) else {'object_guid': object_id}
    obj = await get_address_object(**_filter)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return obj


@router.get("/objects/find_by_kladr/{kladr_code}")
async def object_by_kladr(kladr_code: str):
    """
    <strong>Получить адресный объект по КЛАДР коду</strong>

    Длина КЛАДР кода должна быть 15 символов (без признака актуальности)
    """
    params = await AddressObjectParam.objects.filter(value=kladr_code[:15]).order_by('-start_date').limit(1).all()
    if not params:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    object_id: int = params[0].object_id
    return await object_by_id(object_id)


@router.get("/objects/adm_hierarchy/{object_id_or_guid}")
async def adm_hierarchy(object_id_or_guid: Union[int, str], objects: bool = False, hierarchy: bool = False):
    """
    <strong>Получить административную иерархию объекта по object_id или по object_guid</strong>
    """
    o: Hierarchy = await Hierarchy(AdministrationHierarchy, object_id_or_guid)
    if not o.object_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return o.dict(objects=objects, hierarchy=hierarchy)


@router.get("/objects/mun_hierarchy/{object_id_or_guid}")
async def mun_hierarchy(object_id_or_guid: Union[int, str], objects: bool = False, hierarchy: bool = False):
    """
    <strong>Получить муниципальную иерархию объекта по object_id или по object_guid</strong>
    """
    o: Hierarchy = await Hierarchy(MunHierarchy, object_id_or_guid)
    if not o.object_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return o.dict(objects=objects, hierarchy=hierarchy)


@router.get("/objects/find/adm_hierarchy")
async def find_adm_hierarchy(object_id_or_guid: Optional[Union[int, str]] = None, text: str = '',
                             objects: bool = False, hierarchy: bool = False, limit: Optional[int] = 5):
    """
    <strong>Найти объекты в административной иерархии</strong>

    Для разделения дополнительных номеров дома, использовать ';'
    """
    o: Hierarchy = await Hierarchy(AdministrationHierarchy, object_id_or_guid)
    await o.find(text, limit=limit)
    return o.dict(objects=objects, hierarchy=hierarchy)


@router.get("/objects/find/mun_hierarchy")
async def find_mun_hierarchy(object_id_or_guid: Optional[Union[int, str]] = None, text: str = '',
                             objects: bool = False, hierarchy: bool = False, limit: int = 5):
    """
    <strong>Найти объекты в муниципальной иерархии</strong>

    Для разделения дополнительных номеров дома, использовать ';'
    """
    o: Hierarchy = await Hierarchy(MunHierarchy, object_id_or_guid)
    await o.find(text, limit=limit)
    return o.dict(objects=objects, hierarchy=hierarchy)
