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


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
        

#redirect
@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')


#####################
#- Section related -#
#####################
@app.get("/sections", 
         summary="Get all sections",
         tags=["todo"],
         response_model=list[schemas.Section]
)
async def get_sections(skip: int = 0, limit: int = 100, 
                       session: AsyncSession = Depends(get_async_session), 
                       token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Get all sections
    '''

    return await crud.get_sections(session, token_data.sub, skip, min(limit, 100))

@app.get("/sections/{section_id}", 
         summary="Get one section by ID",
         tags=["todo"],
         response_model=schemas.Section
)
async def get_section_by_id(section_id: int, 
                       session: AsyncSession = Depends(get_async_session), 
                       token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Get section by ID
    '''

    section = await crud.get_section(owner=token_data.sub, section_id=section_id, session=session)
    if section:
        return section
    
    return JSONResponse({"message": "Section not found"}, status_code=404)

@app.delete("/sections/{section_id}", 
         summary="Delete section with tasks in it",
         tags=["todo"]
)
async def delete_section(section_id: int, 
                       session: AsyncSession = Depends(get_async_session), 
                       token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Delete section
    '''

    result = await crud.delete_section(section_id=section_id, owner=token_data.sub, session=session)
    if result:
        return JSONResponse({"message": "Section deleted"}, status_code=200)
    
    return JSONResponse({"message": "Section not found"}, status_code=404)

@app.put("/sections/{section_id}", 
         summary="Update section",
         tags=["todo"],
         response_model=schemas.Section
)
async def update_section_by_id(section_id: int, 
                       section_update: schemas.SectionUpdate,
                       session: AsyncSession = Depends(get_async_session), 
                       token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Update section
    '''

    new_section = await crud.update_section(
        new_section=section_update, 
        owner=token_data.sub,
        section_id=section_id,
        session=session,
    )
    if new_section:
        return new_section
    
    return JSONResponse({"message": "Section not found"}, status_code=404)

@app.post("/sections", 
         summary="Create new sections",
         tags=["todo"],
         response_model=schemas.Section
)
async def create_section(section: schemas.SectionCreate, 
                         session: AsyncSession = Depends(get_async_session), 
                         token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Create section
    '''
    return await crud.create_section(section=section, owner=token_data.sub, session=session)



##################
#- Task related -#
##################
@app.post("/sections/{section_id}/tasks", 
         summary="Upload new task to section",
         tags=["todo"],
         response_model=schemas.Task
)
async def upload_new_task(section_id: int, 
                       task_create: schemas.TaskCreate,
                       session: AsyncSession = Depends(get_async_session), 
                       token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Create new task
    '''

    task = await crud.create_task(
        section_id=section_id,
        task_create=task_create,
        session=session,
        owner=token_data.sub,
    )

    if task:
        return task
    
    return JSONResponse({"message": "Section not found"}, status_code=400)

@app.get("/sections/{section_id}/tasks", 
         summary="Get all tasks",
         tags=["todo"],
         response_model=list[schemas.Task]
)
async def get_tasks(section_id: int, skip: int = 0, limit: int = 100,
                    session: AsyncSession = Depends(get_async_session), 
                    token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Get all tasks
    '''
    return await crud.get_tasks(section_id=section_id, owner=token_data.sub, session=session, skip=skip, limit=limit)

@app.get("/sections/{section_id}/tasks/{task_id}", 
         summary="Get task by ID",
         tags=["todo"],
         response_model=schemas.Task
)
async def get_task(section_id: int,
                    task_id: int,
                    session: AsyncSession = Depends(get_async_session), 
                    token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Get one task
    '''
    task = await crud.get_task(section_id, task_id, token_data.sub, session)
    if task:
        return task
    
    return JSONResponse({"message": "Task or section not found"}, status_code=400)

@app.put("/sections/{section_id}/tasks/{task_id}", 
         summary="Edit task",
         tags=["todo"],
         response_model=schemas.Task
)
async def update_task(section_id: int,
                        task_id: int,
                        task_update: schemas.TaskUpdate,
                        session: AsyncSession = Depends(get_async_session), 
                        token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Update existing task
    '''

    task = await crud.update_task(section_id, task_id, task_update, token_data.sub, session)
    if task:
        return task

    return JSONResponse({"message": "Task or section not found"}, status_code=400)

@app.delete("/sections/{section_id}/tasks/{task_id}", 
         summary="Delete task",
         tags=["todo"]
)
async def delete_task(section_id: int,
                        task_id:int,
                        session: AsyncSession = Depends(get_async_session), 
                        token_data: schemas.TokenData = Depends(JWTBearer())):
    '''
    Delete task
    '''

    result = await crud.delete_task(section_id=section_id, task_id=task_id, owner=token_data.sub, session=session)
    if result:
        return JSONResponse({"message": "Task deleted"}, status_code=200)
    
    return JSONResponse({"message": "Section or task not found"}, status_code=404)