from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.routes import router
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends, HTTPException
from app.core.database import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Document AI Platform",
    description="Medical Device QA Generation API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/health", tags=["System"])
def health_check():
    return JSONResponse(content={"status": "ok"})

@app.get("/health/ready", tags=["System"])
def health_ready(db: Session = Depends(get_db)):
    """
    Ready health check endpoint, verifies DB connectivity.
    """
    try:
        db.execute(text("SELECT 1"))
        return JSONResponse(content={"status": "ready", "db": "connected"})
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")

