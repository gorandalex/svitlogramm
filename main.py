from typing import Callable
from ipaddress import ip_address

from pathlib import Path
import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.orm import Session

from svitlogram.database.connect import get_db
from svitlogram.routes import router
from config import (
    settings,
    PROJECT_NAME,
    VERSION,
    API_PREFIX,
    BANNED_IPS,
    ORIGINS,
)


def get_application():
    """
    The get_application function is a factory function that returns an instance of the FastAPI application.

    :return: The fastapi application
    :doc-author: Trelent
    """
    app = FastAPI(title=PROJECT_NAME, version=VERSION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = get_application()


@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    """
    The ban_ips function is a middleware function that bans IP addresses from accessing the server.
        It takes in a request and call_next, which is the next function to be called after this one.
        The ban_ips function then calls call_next with request as an argument, and returns its response.
    
    :param request: Request: Get the request object
    :param call_next: Callable: Pass the next function in the chain to be called
    :return: A response object
    :doc-author: Trelent
    """
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are used by the application, such as databases or caches.
    
    :return: A coroutine, so we need to run it
    :doc-author: Trelent
    """
    # await FastAPILimiter.init(
    #     await redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password,
    #                       db=0, encoding="utf-8", decode_responses=True)
    # )
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port,

                           db=0, encoding="utf-8", decode_responses=True, password=settings.redis_password) 

                           db=0, encoding="utf-8", decode_responses=True, password=settings.redis_password)

    await FastAPILimiter.init(r)


templates = Jinja2Templates(directory="templates")
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")


@app.get("/", name="Svitlogram_api", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database is configured correctly.
    It does this by executing a query and checking if it returns any results. If it doesn't, then there's something wrong with the database configuration.
    
    :param db: Session: Pass the database session to the function
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    try:
        result = (
            db.execute(text("SELECT 1"))  # noqa
        ).fetchone()

        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")


app.include_router(router, prefix=API_PREFIX)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
