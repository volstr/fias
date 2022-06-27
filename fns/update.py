import asyncio
import zipfile

from core.database import database
from fns.import_gar import GarImport
from gar.models import AlembicVersion, Updates


async def current_version():
    alembic_version = (await AlembicVersion.objects.first()).version_num
    version: int = await Updates.objects.filter(state='Выполнено').max(columns=["id"])

    print('alembic_version:', alembic_version, 'version:', version)


async def main():
    if not database.is_connected:
        await database.connect()

    await current_version()

    zip_name = r'D:\Project\KMIAC\PyFIAS\updates\20211112_gar_xml.zip'

    with zipfile.ZipFile(zip_name, mode='r', allowZip64=True) as archive:
        gar = GarImport(archive, 23)
        await gar.import_all()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(1)
