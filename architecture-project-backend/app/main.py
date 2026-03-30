from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware

from shared.config import settings
from shared.exceptions import ApplicationException
from infrastructure.database import Database
from features.items.router import router as items_router
from features.users.router import router as users_router

database = Database()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.prepopulate_database()
    yield


app = FastAPI(title="Architecture Template API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(DBSessionMiddleware, db_url=database.get_connection_info())

app.include_router(items_router, prefix="/items")
app.include_router(users_router, prefix="/users")


@app.exception_handler(ApplicationException)
async def application_exception_handler(request: Request, exc: ApplicationException):
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "message": exc.message,
            "details": exc.details,
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "details": str(exc),
            "path": str(request.url),
        },
    )


@app.get("/", tags=["health"])
def health_check():
    return {"status": "OK"}
