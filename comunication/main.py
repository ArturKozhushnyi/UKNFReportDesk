"""
Communication Service - Chat/Messaging System
Handles conversations, messages, participants, tags, attachments, read receipts, reactions, and assignments
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.routers import chat


# Read environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Create engine and SessionLocal
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup: verify database connection
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))
        print("Database connection verified")
    
    yield
    
    # Shutdown: dispose engine resources
    engine.dispose()


app = FastAPI(
    title="Communication Service",
    description="Chat and messaging system for UKNF Report Desk",
    version="1.0.0",
    lifespan=lifespan
)

# Include chat router
app.include_router(chat.router, prefix="/api")


def get_db():
    """Dependency for obtaining database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "service": "communication-service",
        "version": "1.0.0"
    }


@app.get("/healthz")
def healthz():
    """Health check endpoint with database verification"""
    from sqlalchemy import text
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "up"}
    except Exception as e:
        return {"status": "unhealthy", "database": "down", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

