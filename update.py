import asyncio
import os.path
import time
import zipfile

import schedule

from core.database import database
from core.log import get_logger
from core.settings import settings
from fns.download import get_updates_file_list, download_update
from fns.import_gar import GarImport
from gar.models import AlembicVersion, Updates


async def update():
    if not database.is_connected:
        await database.connect()

    alembic_version = (await AlembicVersion.objects.first()).version_num
    if not alembic_version:
        raise ValueError('Не выполнены миграции')
    version: int = await Updates.objects.filter(state='Выполнено').max(columns=["id"])

    update_list = get_updates_file_list(version)
    for url_obj in update_list:
        update_file = download_update(url_obj, version is not None)
        zip_name = update_file['File']

        with zipfile.ZipFile(zip_name, mode='r', allowZip64=True) as archive:
            gar = GarImport(archive, settings.update.region)
            await gar.import_all()

        try:
            os.remove(zip_name)
        except OSError:
            pass


def main():
    asyncio.run(update())

    if settings.update.check and settings.update.time:
        schedule.every().day.at(settings.update.time).do(lambda: asyncio.run(update()))

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    try:
        if not os.path.isfile(settings.file_name):
            raise FileNotFoundError(f'Не найден файл настроек: {settings.file_name}')
    except FileNotFoundError as e:
        get_logger('import').critical(str(e))
        raise e

    try:
        main()
    except KeyboardInterrupt:
        exit(1)
