import logging, typing
import json

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import config, schemas, group_crud
from .utils import HashContext
from .database import get_async_session, models, DB_INITIALIZER


#init logger
logger = logging.getLogger("user-service")
logging.basicConfig(
    level=20,
    format="%(levelname)-9s %(message)s"
)

#load config
cfg: config.Config = config.load_config(_env_file='.env')
logger.info(
    'Service configuration loaded:\n' +
    f'{cfg.model_dump_json(by_alias=True, indent=4)}'
)

hash_context = HashContext(cfg.JWT_SECRET, cfg.JWT_REFRESH_SECRET)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Database initialization...{cfg.PG_ASYNC_DSN.unicode_string()}")
    await DB_INITIALIZER.init_db(
        cfg.PG_ASYNC_DSN.unicode_string()
    )

    groups = []
    with open(cfg.DEFAULT_GROUPS_CONFIG_PATH) as f:
        groups = json.load(f)

    logger.info(f"Loaded default groups: {groups}")
    async for session in get_async_session():
        for group in groups:
            await group_crud.upsert_group(
                session, schemas.GroupUpsert(**group)
            )
    yield
    #here you can clear data


#create app
app = FastAPI(
    version='0.0.1',
    title='User service',
    lifespan=lifespan
)


@app.post("/auth/register", 
         summary="Register",
         tags=["auth"]
)
async def login(data: schemas.CreateUserSchema, session: AsyncSession = Depends(get_async_session)):
    existing_user = models.get_user_db(session, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    user = {
        'email': data.email,
        'nickname': data.nickname,
        'hashed_password': hash_context.get_hashed_password(data.password),
        'group_id': 0 #user by default
    }

    new_user = models.User(**user)
    session.add(new_user)
    await session.commit()

    return JSONResponse(content={"message": "User created successfully"})

@app.get(
    "/groups",
    summary='Возвращает список групп пользователей',
    response_model=list[schemas.GroupRead],
    tags=["groups"]
)
async def get_group_list(
        session: AsyncSession = Depends(get_async_session),
        skip: int = 0,
        limit: int = 100
    ) -> typing.List[schemas.GroupRead]:

    return await group_crud.get_groups(session, skip, limit)


@app.get("/groups/{group_id}", summary='Возвращает информацию о группе пользователей', tags=["groups"])
async def get_group_info(
        group_id: int, session: AsyncSession = Depends(get_async_session)
    ) -> schemas.GroupRead :
    
    group = await group_crud.get_group(session, group_id)
    if group != None:
        return group
    return JSONResponse(status_code=404, content={"message": "Item not found"})


@app.put("/groups/{group_id}", summary='Обновляет информацию о группе пользователей', tags=["groups"])
async def update_group(
        group_id: int, 
        group: schemas.GroupUpdate,
        session: AsyncSession = Depends(get_async_session)
    ) -> schemas.GroupRead:

    group = await group_crud.update_group(session, group_id, group)
    if group != None:
        return group
    return JSONResponse(status_code=404, content={"message": "Item not found"})