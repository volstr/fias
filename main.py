from fastapi import FastAPI, APIRouter

from core.database import database
from gar import models
from gar.views import router as router_gar

app = FastAPI()
router = APIRouter()

# app.state.database = database


@app.get("/hello/{name}")
async def say_hello(name: str):
    return await models.Level.objects.create(name=name)


@app.on_event("startup")
async def startup() -> None:
    if not database.is_connected:
        await database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    if database.is_connected:
        await database.disconnect()


@app.on_event("startup")
async def main() -> None:
    # import subprocess
    # import sys
    #
    # command = 'fns\\update.py'
    #
    # # Запуск обновления
    # sp = subprocess.Popen(f'{sys.executable} {command}')
    # print('subprocess OK')
    # print(sp)

    pass


router.include_router(router_gar)
app.include_router(router)
