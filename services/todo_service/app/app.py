import logging, typing, jwt


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import config, schemas, crud
from .jwtbearer import JWTBearer
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Database initialization...{cfg.PG_ASYNC_DSN.unicode_string()}")
    await DB_INITIALIZER.init_db(
        cfg.PG_ASYNC_DSN.unicode_string()
    )
    yield
    #here you can clear data


#create app
app = FastAPI(
    version='0.0.1',
    title='Todo service',
    lifespan=lifespan
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
        

#redirect
@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')


@app.get("/sections", 
         summary="Get all sections",
         tags=["todo"],
         response_model=list[schemas.Section]
)
async def get_sections(skip: int = 0, limit: int = 100, 
                       session: AsyncSession = Depends(get_async_session), 
                       token_data: schemas.TokenData = Depends(JWTBearer())):
    return await crud.get_sections(session, token_data.sub, skip, min(limit, 100))

@app.get("/sections/{section_id}", 
         summary="Get one section by ID",
         tags=["todo"],
         response_model=schemas.Section
)
async def get_section_by_id(section_id: int, 
                       session: AsyncSession = Depends(get_async_session), 
                       token_data: schemas.TokenData = Depends(JWTBearer())):
    section = await crud.get_section(owner=token_data.sub, section_id=section_id, session=session)
    if section:
        return section
    
    return JSONResponse({"message": "Not found"}, status_code=404)

@app.put("/sections/{section_id}", 
         summary="Update section",
         tags=["todo"],
         response_model=schemas.Section
)
async def get_section_by_id(section_id: int, 
                       section_update: schemas.SectionUpdate,
                       session: AsyncSession = Depends(get_async_session), 
                       token_data: schemas.TokenData = Depends(JWTBearer())):
    new_section = await crud.update_section(
        new_section=section_update, 
        owner=token_data.sub,
        section_id=section_id,
        session=session,
    )
    if new_section:
        return new_section
    
    return JSONResponse({"message": "Not found"}, status_code=404)

@app.post("/sections", 
         summary="Create new sections",
         tags=["todo"],
         response_model=schemas.Section
)
async def create_section(section: schemas.SectionCreate, 
                         session: AsyncSession = Depends(get_async_session), 
                         token_data: schemas.TokenData = Depends(JWTBearer())):
    return await crud.create_section(section=section, owner=token_data.sub, session=session)