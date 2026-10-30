from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine
from app.routers.projects import router as projects_router


app = FastAPI(
    title="Aadi Portfolio API",
    version="1.0.0",
)
app.include_router(projects_router)



@app.get("/")
def root():
    return {"message": "Aadi Portfolio API is running"}


@app.get("/api/v1/health/database")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"status": "connected"}

    except SQLAlchemyError:
        return {"status": "unavailable"}