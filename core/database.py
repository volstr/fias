import databases
import ormar
import sqlalchemy

from core.settings import settings


def get_connection_url() -> str:
    """ Получить строку подключения к базе данных """
    db = settings.database
    if db.driver_name == db.DriverName.sqlite:
        return f"sqlite:///{settings.database.base}"
    elif db.driver_name in {db.DriverName.postgresql, db.DriverName.mysql}:
        port = f':{db.port}' if db.port else ""
        return f'{db.driver_name}://{db.user}:{db.password}@{db.host}{port}/{db.base}'
    else:
        raise Exception("Не верно указан драйвер БД")


database = databases.Database(get_connection_url())
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    """ Базовый класс Meta модели """
    metadata = metadata
    database = database


def replace_database():
    pass
    # from core.database import metadata, database
    # s = await models.Item.objects.all()
    #
    # DATABASE_URL = "sqlite:///test2.db"
    # # engine = sqlalchemy.create_engine(DATABASE_URL)
    # # # just to be sure we clear the db before
    # # metadata.drop_all(engine)
    # # # yield
    # # metadata.create_all(engine)
    #
    # # database.disconnect()
    # # database.url = DATABASE_URL
    # import databases
    # database = databases.Database(DATABASE_URL)
    # await database.connect()
    #
    # # models.Item.Meta.database = database
    #
    # for i in metadata.sorted_tables:
    #     print(i)
    #     # i.Meta.database = database
    #
    # return s
