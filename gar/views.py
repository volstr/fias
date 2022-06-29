from typing import List, Optional, Union

from fastapi import APIRouter

from gar.models import Level, AddressType, ParamType, HouseType, ApartmentType, Updates
from gar.schemas import LevelSchema, DirectorySchema, ParamTypeSchema, AddressTypeSchema, UpdatesSchema

router = APIRouter(prefix='/api', tags=['ГАР / ФИАС'])


@router.get("/levels", response_model=List[LevelSchema])
async def levels():
    """
    Сведения по уровням адресных объектов
    """
    return await Level.objects.all()


@router.get("/house_types", response_model=List[DirectorySchema])
async def house_types():
    """
    Признаки владения
    """
    return await HouseType.objects.all()


@router.get("/apartment_types", response_model=List[DirectorySchema])
async def house_types():
    """
    Признаки владения
    """
    return await ApartmentType.objects.all()


@router.get("/param_types", response_model=List[ParamTypeSchema])
async def param_types():
    """
    Сведения по типу параметра
    """
    return await ParamType.objects.all()


@router.get("/address_types", response_model=List[AddressTypeSchema])
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
