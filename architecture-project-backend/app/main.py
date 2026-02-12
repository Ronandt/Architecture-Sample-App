from fastapi import FastAPI
#from app.core.database import Base, engine
#from app.features.users.router import router as users_router

app = FastAPI(title="SCVU API")

# Create tables (for development)
#Base.metadata.create_all(bind=engine)

# Register routers
#app.include_router(users_router)

@app.get("/")
def health_check():
    return {"status": "OK"}