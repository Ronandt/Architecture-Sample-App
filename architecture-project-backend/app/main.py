from fastapi import FastAPI
from infrastructure.database import Database
from fastapi_sqlalchemy import DBSessionMiddleware, db

app = FastAPI(title="SCVU API")
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