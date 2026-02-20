from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from shared.exceptions import ApplicationException
from infrastructure.database import Database
from fastapi_sqlalchemy import DBSessionMiddleware, db

app = FastAPI(title="SCVU API")

async def global_exception_handler(request: Request, exc: ApplicationException):
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "message": exc.message,
            "details": exc.details,
            "path": str(request.url)
        }
    )

# Global handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "details": str(exc),
            "path": str(request.url)
        }
    )


database = Database()

app.add_middleware(DBSessionMiddleware, db_url = database.get_connection_info())


@app.on_event("startup")
def startup_event():
    database.prepopulate_database()

# Register routers
#app.include_router(users_router)

@app.get("/")
def health_check():
    return {"status": "OK"}