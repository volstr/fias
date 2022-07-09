import asyncio

from fastapi import FastAPI, APIRouter

from core.database import database
from gar.models import Updates, AlembicVersion
from gar.views import router as router_gar, router_types

app = FastAPI()
router = APIRouter()

# app.state.database = database


@app.get("/version")
async def version():
    tasks = [
        Updates.objects.filter(state='Выполнено').max('id'),
        AlembicVersion.objects.first()
    ]
    max_id, alembic_version, *_ = await asyncio.gather(*tasks)

    return {
        'version': max_id,
        'migration': alembic_version.version_num
    }


@app.on_event("startup")
async def startup() -> None:
    if not database.is_connected:
        await database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    if database.is_connected:
        await database.disconnect()


router.include_router(router_types)
router.include_router(router_gar)
app.include_router(router)
