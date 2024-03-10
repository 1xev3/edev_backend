import logging, typing
import json

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse, RedirectResponse

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import config, schemas, group_crud
from .utils import HashContext, JWTBearer
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

#revoke tokens. you can use redis for that in prod
hash_context = HashContext(cfg.JWT_SECRET.get_secret_value(), cfg.JWT_REFRESH_SECRET.get_secret_value())

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

#redirect
@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')

#login form, get current user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
async def get_current_user(session: AsyncSession = Depends(get_async_session), data: str = Depends(oauth2_scheme)):
    acc = hash_context.decode_access_token(data)

    if acc:
        email = acc["sub"]
        return await models.get_user_db(session, email)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )





@app.post("/auth/register", 
         summary="Register",
         tags=["auth"]
)
async def register(data: schemas.CreateUserSchema, session: AsyncSession = Depends(get_async_session)):
    existing_user = await models.get_user_db(session, data.email)
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



@app.get("/users/me",tags=["users"])
async def users_me(user: models.User = Depends(get_current_user)) -> schemas.UserSchema:
    return user

@app.patch("/users/me",tags=["users"])
async def users_me(update_user: schemas.UserUpdateSchema, user: models.User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)) -> schemas.UserSchema:
    user.nickname = update_user.nickname
    user.hashed_password = hash_context.get_hashed_password(update_user.password)

    session.add(user)
    await session.commit()

    return user

@app.post("/auth/logout",tags=["auth"])
async def logout(token: str = Depends(oauth2_scheme)) -> schemas.UserSchema:
    hash_context.add_token_to_deny_list(token)
    return JSONResponse(content={"message": "Exited"})



@app.post('/auth/login', 
          summary="Create access and refresh tokens for user", 
          response_model=schemas.TokenSchema,
          tags=["auth"]
          )
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_async_session)):
    email = form_data.username
    user = await models.get_user_db(session, email)
    
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Incorrect email or password",
            }
        )

    hashed_pass = user.hashed_password
    if not hash_context.verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
        
    
    return {
        "access_token": hash_context.create_access_token(user),
        "refresh_token": hash_context.create_refresh_token(user),#can be used after
    }







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