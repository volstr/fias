import asyncio
import collections
import os
import zipfile
from datetime import datetime
from typing import List, Any, Optional

from core.log import import_log
from core.settings import settings
from fns.gar_xml import rows_from_xml
from gar.models import Level, AddressObject, AddressType, ParamType, AdministrationHierarchy, AddressObjectParam, \
    HouseType, House, ApartmentType, Apartment, MunHierarchy, Updates


class GarImportBase:
    def __init__(self, archive: zipfile.ZipFile, region: Optional[int] = None) -> None:
        self.log = import_log
        # Для sqlite размер загружаемого блока - 50, для остальных 1000
        self.block_length = 50 if settings.database.driver_name == settings.database.DriverName.sqlite else 1000
        assert region is None or 0 < region < 100, 'Не корректно указан регион'
        self.archive = archive
        self.region = region
        self._version: int = int(os.path.basename(self.archive.filename)[:8])

        # Модели, в которых будем проверять наличие object_id, для того, что бы не загружать лишние зависимости.
        self._checked_models = (AddressObject, House, Apartment, )

        self._load_file_list()

    @property
    def version(self):
        """ Получить версию файла обновления из имени файла """
        return self._version

    def _load_file_list(self) -> None:
        region = f'{self.region:0=2}' if self.region else ''

        def get_files_by_mask(mask: str) -> List[str]:
            return [x for x in file_list if mask in x]

        file_list = sorted(self.archive.namelist())
        self._file_levels: str = get_files_by_mask('AS_OBJECT_LEVELS_202')[0]
        self._file_address_object_type: str = get_files_by_mask('AS_ADDR_OBJ_TYPES_202')[0]
        self._file_param_type: str = get_files_by_mask('AS_PARAM_TYPES_202')[0]
        self._file_house_type: str = get_files_by_mask('AS_HOUSE_TYPES_202')[0]
        self._file_apartment_type: str = get_files_by_mask('AS_APARTMENT_TYPES_202')[0]
        self._file_address_object: List[str] = get_files_by_mask(f'{region}/AS_ADDR_OBJ_202')
        self._file_house: List[str] = get_files_by_mask(f'{region}/AS_HOUSES_202')
        self._file_apartment: List[str] = get_files_by_mask(f'{region}/AS_APARTMENTS_202')
        self._file_adm_hierarchy: List[str] = get_files_by_mask(f'{region}/AS_ADM_HIERARCHY_202')
        self._file_mun_hierarchy: List[str] = get_files_by_mask(f'{region}/AS_MUN_HIERARCHY_202')
        self._file_object_param: List[str] = get_files_by_mask(f'{region}/AS_ADDR_OBJ_PARAMS_202')

    async def _commit_updates(self, model, items, is_exist: bool, file: str, check_object_id: bool = False) -> None:
        if check_object_id:
            checked_object_id_list = []
            object_id_list = [x.object_id for x in items]
            for i in self._checked_models:
                # Проверяем, если ли это у нас в базе на то что ссылаемся
                checked_object_id_list.extend(
                    await i.objects.filter(object_id__in=object_id_list).values_list('object_id', flatten=True)
                )

            items = [x for x in items if x.object_id in checked_object_id_list]

        if not items:
            # Выходим если нечего добавлять/обновлять
            return

        if not is_exist:
            # Если изначально таблица пустая - ничего проверять не будем, просто добавляем
            await self._bulk_create(file, model, items)
        else:
            # Таблица не пустая, разбираемся что добавлять, а что обновлять
            id_from_arch: set = {x.id for x in items}
            id_from_db: list = await model.objects.filter(id__in=id_from_arch).values_list('id', flatten=True)

            id_to_insert = id_from_arch - set(id_from_db)
            id_to_update = id_from_arch - id_to_insert

            if id_to_update:
                await self._bulk_update(file, model, [x for x in items if x.id in id_to_update])
            if id_to_insert:
                await self._bulk_create(file, model, [x for x in items if x.id in id_to_insert])

    async def _bulk_create(self, file: str, model: Any, items: List) -> None:
        try:
            await model.objects.bulk_create(items)
        except Exception as block_except:
            # Ошибка при добавлении блока. Пробуем добавлять по одной записи
            self.log.warning(f'Ошибка при добавлении блока. {file}. Добавляем по одной записи: {block_except}')
            for i in items:
                try:
                    await model.objects.create(**i.dict())
                except Exception as e:
                    self.log.error(f'File {file}.\n\tItem: {i.dict()}\n{e}')

    async def _bulk_update(self, file: str, model: Any, items: List) -> None:
        try:
            await model.objects.bulk_update(items)
        except Exception as block_except:
            # Ошибка при изменении блока. Пробуем изменять по одной записи
            self.log.warning(f'Ошибка при изменении блока. {file}. Изменяем по одной записи: {block_except}')
            for i in items:
                try:
                    await model.objects.bulk_update([i])
                except Exception as e:
                    self.log.error(f'File {file}.\n\tItem: {i.dict()}\n{e}')

    async def _import_model(self, model, file_name: str, callback: Any, check_object_id: bool = False) -> None:
        items = collections.deque()
        # Определяем тип модели
        is_exist = await model.objects.exists()
        for idx, i in enumerate(rows_from_xml(self.archive, file_name)):
            value = callback(i)
            if value:
                items.append(value)
                # Добавляем/обновляем блоками по 1000 записей
                if len(items) >= self.block_length:
                    await self._commit_updates(model, items, is_exist, file_name, check_object_id)
                    items.clear()
        # Добавляем оставшееся
        await self._commit_updates(model, items, is_exist, file_name, check_object_id)


class GarImport(GarImportBase):
    def __init__(self, archive: zipfile.ZipFile, region: Optional[int] = None) -> None:
        super().__init__(archive, region)

    async def import_level(self):
        self.log.info(f'Импорт сведений по уровням адресных объектов (AS_OBJECT_LEVELS)...')
        file_name = self._file_levels
        assert 'AS_OBJECT_LEVELS_202' in file_name, f'{file_name} не OBJECT_LEVELS'

        def parse(item) -> Level:
            return Level(
                id=item.get('@LEVEL'),
                name=item.get('@NAME'),
                # short_name=item.get('@SHORTNAME'),
                start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                is_active=item.get('@ISACTIVE') == 'true'
            )
        await self._import_model(Level, file_name, parse)

    async def import_address_type(self):
        self.log.info(f'Импорт сведений по типам адресных объектов (AS_ADDR_OBJ_TYPES)...')
        file_name = self._file_address_object_type
        assert 'AS_ADDR_OBJ_TYPES_202' in file_name, f'{file_name} не ADDR_OBJ_TYPES'

        def parse(item) -> AddressType:
            return AddressType(
                    id=item.get('@ID'),
                    level_id=int(item.get('@LEVEL')),
                    name=item.get('@NAME'),
                    short_name=item.get('@SHORTNAME'),
                    description=item.get('@DESC'),
                    update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                    start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                    end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                    is_active=item.get('@ISACTIVE') == 'true'
                )
        await self._import_model(AddressType, file_name, parse)

    async def import_param_types(self):
        self.log.info(f'Импорт сведений по типу параметра (AS_PARAM_TYPES)...')
        file_name = self._file_param_type
        assert 'AS_PARAM_TYPES_202' in file_name, f'{file_name} не PARAM_TYPES'

        def parse(item) -> ParamType:
            return ParamType(
                id=item.get('@ID'),
                name=item.get('@NAME'),
                code=item.get('@CODE'),
                description=item.get('@DESC') if item.get('@DESC') else None,
                update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                is_active=item.get('@ISACTIVE') == 'true'
            )
        await self._import_model(ParamType, file_name, parse)

    async def import_house_types(self):
        self.log.info(f'Импорт сведений по признакам владения (AS_HOUSE_TYPES)...')
        file_name = self._file_house_type
        assert 'AS_HOUSE_TYPES_202' in file_name, f'{file_name} не HOUSE_TYPES'

        def parse(item) -> HouseType:
            return HouseType(
                id=item.get('@ID'),
                name=item.get('@NAME'),
                short_name=item.get('@SHORTNAME'),
                description=item.get('@DESC') if item.get('@DESC') else None,
                update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                is_active=item.get('@ISACTIVE') == 'true'
            )
        await self._import_model(HouseType, file_name, parse)

    async def import_apartment_types(self):
        self.log.info(f'Импорт сведений по типам помещений (AS_APARTMENT_TYPES)...')
        file_name = self._file_apartment_type
        assert 'AS_APARTMENT_TYPES_202' in file_name, f'{file_name} не AS_APARTMENT_TYPES'

        def parse(item) -> ApartmentType:
            return ApartmentType(
                id=item.get('@ID'),
                name=item.get('@NAME'),
                short_name=item.get('@SHORTNAME'),
                description=item.get('@DESC') if item.get('@DESC') else None,
                update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                is_active=item.get('@ISACTIVE') == 'true'
            )
        await self._import_model(ApartmentType, file_name, parse)

    async def import_address_object(self):
        self.log.info(f'Импорт классификатора адресообразующих элементов: регионы, города, улицы (AS_ADDR_OBJ)...')

        def parse(item) -> Optional[AddressObject]:
            if int(item.get('@NEXTID', 0)) == 0 and item.get('@NAME'):
                # Выбираем только актуальные записи
                return AddressObject(
                    id=item.get('@ID'),
                    object_id=item.get('@OBJECTID'),
                    object_guid=item.get('@OBJECTGUID'),
                    name=item.get('@NAME'),
                    type_name=item.get('@TYPENAME'),
                    level_id=int(item.get('@LEVEL')),
                    update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                    start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                    end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                    is_actual=item.get('@ISACTUAL') == '1',
                    is_active=item.get('@ISACTIVE') == '1',
                )

        tasks = [
            asyncio.create_task(self._import_model(AddressObject, file_name, parse))
            for file_name in self._file_address_object
        ]
        await asyncio.gather(*tasks)

    async def import_houses(self):
        self.log.info(f'Импорт сведений по номерам домов улиц городов и населенных пунктов (AS_HOUSE)...')

        def parse(item: dict) -> Optional[House]:
            if int(item.get('@NEXTID', 0)) == 0:
                # Выбираем только актуальные записи
                if int(item.get('@HOUSETYPE', 0)) < 0:
                    # Пропускаем записи, нарушающие ограничения внешнего ключа
                    return
                return House(
                    id=item.get('@ID'),
                    object_id=item.get('@OBJECTID'),
                    object_guid=item.get('@OBJECTGUID'),
                    house_num=item.get('@HOUSENUM'),
                    add_num1=item.get('@ADDNUM1'),
                    add_num2=item.get('@ADDNUM2'),
                    house_type=int(item.get('@HOUSETYPE')) if item.get('@HOUSETYPE') else None,
                    add_type1=int(item.get('@ADDTYPE1')) if item.get('@ADDTYPE1') else None,
                    add_type2=int(item.get('@ADDTYPE2')) if item.get('@ADDTYPE2') else None,
                    update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                    start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                    end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                    is_actual=item.get('@ISACTUAL') == '1',
                    is_active=item.get('@ISACTIVE') == '1',
                )

        tasks = [
            asyncio.create_task(self._import_model(House, file_name, parse))
            for file_name in self._file_house
        ]
        await asyncio.gather(*tasks)

    async def import_apartments(self):
        self.log.info(f'Импорт сведений по помещениям (AS_APARTMENTS)...')

        def parse(item) -> Optional[Apartment]:
            if int(item.get('@NEXTID', 0)) == 0:
                # Выбираем только актуальные записи
                return Apartment(
                    id=item.get('@ID'),
                    object_id=int(item.get('@OBJECTID')),
                    object_guid=item.get('@OBJECTGUID'),
                    number=item.get('@NUMBER'),
                    apartment_type_id=abs(int(item.get('@APARTTYPE'))),
                    is_actual=item.get('@ISACTUAL') == '1',
                    update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                    start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                    end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                    is_active=item.get('@ISACTIVE') == '1'
                )
        tasks = [
            asyncio.create_task(self._import_model(Apartment, file_name, parse))
            for file_name in self._file_apartment
        ]
        await asyncio.gather(*tasks)

    async def import_administration_hierarchy(self):
        self.log.info(f'Импорт сведений по иерархии в административном делении (AS_ADM_HIERARCHY)...')

        def parse(item) -> Optional[AdministrationHierarchy]:
            if int(item.get('@NEXTID', 0)) == 0:
                # Выбираем только актуальные записи
                return AdministrationHierarchy(
                    id=item.get('@ID'),
                    object_id=int(item.get('@OBJECTID')),
                    parent_object_id=None if item.get('@PARENTOBJID', '0') == '0' else int(item.get('@PARENTOBJID')),
                    region_code=None if item.get('@REGIONCODE') == '0' else item.get('@REGIONCODE'),
                    area_code=None if item.get('@AREACODE') == '0' else item.get('@AREACODE'),
                    city_code=None if item.get('@CITYCODE') == '0' else item.get('@CITYCODE'),
                    place_code=None if item.get('@PLACECODE') == '0' else item.get('@PLACECODE'),
                    plan_code=None if item.get('@PLANCODE') == '0' else item.get('@PLANCODE'),
                    street_code=None if item.get('@STREETCODE') == '0' else item.get('@STREETCODE'),
                    update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                    start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                    end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                    is_active=item.get('@ISACTIVE') == '1'
                )
        tasks = [
            asyncio.create_task(self._import_model(AdministrationHierarchy, file_name, parse, True))
            for file_name in self._file_adm_hierarchy
        ]
        await asyncio.gather(*tasks)

    async def import_mun_hierarchy(self):
        self.log.info(f'Импорт сведений по иерархии в муниципальном делении (AS_MUN_HIERARCHY)...')

        def parse(item) -> Optional[MunHierarchy]:
            if int(item.get('@NEXTID', 0)) == 0:
                # Выбираем только актуальные записи
                return MunHierarchy(
                    id=item.get('@ID'),
                    object_id=int(item.get('@OBJECTID')),
                    parent_object_id=None if item.get('@PARENTOBJID', '0') == '0' else int(item.get('@PARENTOBJID')),
                    oktmo=item.get('@OBJECTID'),
                    path=item.get('@PATH'),
                    update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                    start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                    end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                    is_active=item.get('@ISACTIVE') == '1'
                )
        tasks = [
            asyncio.create_task(self._import_model(MunHierarchy, file_name, parse, True))
            for file_name in self._file_mun_hierarchy
        ]
        await asyncio.gather(*tasks)

    async def import_address_object_param(self):
        self.log.info(f'Импорт сведений по типу параметра (КЛАДР) (AS_ADDR_OBJ_PARAMS)...')

        def parse(item) -> Optional[AddressObjectParam]:
            type_id = int(item.get('@TYPEID'))
            if type_id in {5, 10, 16} and int(item.get('@CHANGEIDEND', 0)) == 0:
                # Читаем КЛАДР из списка с признаком актуальности и убираем этот признак.
                # Можно было бы брать сразу из списка с TYPEID == 11, но он у них давно не обновлялся
                return AddressObjectParam(
                        id=item.get('@ID'),
                        object_id=int(item.get('@OBJECTID')),
                        param_type_id=11 if type_id == 10 else type_id,
                        value=item.get('@VALUE')[:-2] if type_id == 10 else item.get('@VALUE')[:128],
                        update_date=datetime.strptime(item.get('@UPDATEDATE'), "%Y-%m-%d").date(),
                        start_date=datetime.strptime(item.get('@STARTDATE'), "%Y-%m-%d").date(),
                        end_date=datetime.strptime(item.get('@ENDDATE'), "%Y-%m-%d").date(),
                    )
        tasks = [
            asyncio.create_task(self._import_model(AddressObjectParam, file_name, parse, True))
            for file_name in self._file_object_param
        ]
        await asyncio.gather(*tasks)

    async def import_all(self):
        """
        Импорт всех данных из архива
        """
        str_region = f'Регион: {self.region:0=2}' if self.region else ''
        self.log.info(f'Импорт ГАР/ФИАС. Файл {self.archive.filename}. {str_region}')

        update = Updates(id=self.version, state='Выполняется')
        await self._commit_updates(Updates, [update], True, 'updates')

        try:
            await self.import_level()
            await self.import_address_type()
            await self.import_param_types()
            await self.import_house_types()
            await self.import_apartment_types()

            await self.import_address_object()
            if settings.update.level in (settings.update.Level.home, settings.update.Level.apartment):
                await self.import_houses()
            if settings.update.level in (settings.update.Level.apartment, ):
                await self.import_apartments()

            if settings.update.hierarchy in (settings.update.Hierarchy.administration, settings.update.Hierarchy.all):
                await self.import_administration_hierarchy()
            if settings.update.hierarchy in (settings.update.Hierarchy.municipal, settings.update.Hierarchy.all):
                await self.import_mun_hierarchy()
            await self.import_address_object_param()

            update = Updates(id=self.version, state='Выполнено')
            await self._commit_updates(Updates, [update], True, 'updates')
        except Exception as e:
            update = Updates(id=self.version, state='Ошибка')
            await self._commit_updates(Updates, [update], True, 'updates')
            self.log.critical(f'{e}')
            raise e
        finally:
            self.log.info('Импорт завершен')
