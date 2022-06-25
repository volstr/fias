from fastapi import FastAPI

from core import database
from fns.import_gar import UpdateFile
from gar import models

app = FastAPI()

# engine = sqlalchemy.engine.create_engine("sqlite:///test2.db")
# metadata.create_all(engine)
# # app.state.database = database


# @app.get("/", response_model=List[models.Item])
@app.get("/")
async def root():
    return await models.Level.objects.limit(100).all()


@app.get("/hello/{name}")
async def say_hello(name: str):
    return await models.Level.objects.create(name=name)


@app.on_event("startup")
async def startup() -> None:
    # database_: Database = app.state.database
    # if not database_.is_connected:
    #     await database_.connect()
    if not database.database.is_connected:
        await database.database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    # database_: Database = app.state.database
    # if database_.is_connected:
    #     await database_.disconnect()
    if database.database.is_connected:
        await database.database.disconnect()


@app.on_event("startup")
async def main() -> None:
    file_name = r'D:\Project\KMIAC\PyFIAS\updates\20211112_gar_xml.zip'
    d = UpdateFile(file_name)
    await d.load_file_list(file_name)
