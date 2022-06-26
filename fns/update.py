import asyncio
import zipfile

from core.database import database
from fns.import_gar import GarImport


async def main():
    zip_name = r'D:\Project\KMIAC\PyFIAS\updates\20211112_gar_xml.zip'

    if not database.is_connected:
        await database.connect()

    with zipfile.ZipFile(zip_name, mode='r', allowZip64=True) as archive:
        gar = GarImport(archive, 23)
        await gar.import_all()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(1)
