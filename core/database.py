import databases
import ormar
import sqlalchemy

# https://github.com/joshua-hashimoto/fastapi-ormar


def get_connection_url() -> str:
    """ Получить строку подключения к базе данных """
    print('database')
    # return "sqlite:///test.db"

    host = 'localhost'
    user = 'postgres'
    password = 'qwerty'
    db = 'gar'
    return f'postgresql://{user}:{password}@{host}:5432/{db}'


# metadata = sqlalchemy.MetaData()

# # create the database
# # note that in production you should use migrations
# # note that this is not required if you connect to existing database
# DATABASE_URL = "sqlite:///test.db"
# engine = sqlalchemy.create_engine(DATABASE_URL)
# # just to be sure we clear the db before
# metadata.drop_all(engine)
# metadata.create_all(engine)


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

