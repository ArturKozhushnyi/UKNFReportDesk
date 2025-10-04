import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import (
    create_engine, text, MetaData, Table, Column,
    BigInteger, String, Boolean, DateTime, insert, select
)
from sqlalchemy.orm import sessionmaker, Session


# Read DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Create engine and SessionLocal
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Define metadata and SUBJECTS table
metadata = MetaData()

subjects = Table(
    "SUBJECTS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("TYPE_STRUCTURE", String(250)),
    Column("CODE_UKNF", String(250)),
    Column("NAME_STRUCTURE", String(500)),
    Column("LEI", String(20)),
    Column("NIP", String(10)),
    Column("KRS", String(10)),
    Column("STREET", String(250)),
    Column("NR_STRET", String(250)),
    Column("NR_HOUSE", String(250)),
    Column("POST_CODE", String(250)),
    Column("TOWN", String(250)),
    Column("PHONE", String(250)),
    Column("EMAIL", String(500)),
    Column("UKNF_ID", String(100)),
    Column("STATUS_S", String(250)),
    Column("KATEGORY_S", String(500)),
    Column("SELEKTOR_S", String(500)),
    Column("SUBSELEKTOR_S", String(500)),
    Column("TRANS_S", Boolean),
    Column("DATE_CREATE", DateTime(timezone=True)),
    Column("DATE_ACTRUALIZATION", DateTime(timezone=True)),
)

users = Table(
    "USERS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("USER_NAME", String(250)),
    Column("USER_LASTNAME", String(250)),
    Column("PHONE", String(250)),
    Column("EMAIL", String(500)),
    Column("PESEL", String(11)),
    Column("PASSWORD_HASH", String(64)),
    Column("IS_USER_ACTIVE", Boolean),
    Column("UKNF_ID", String(100)),
    Column("DATE_CREATE", DateTime(timezone=True)),
    Column("DATE_ACTRUALIZATION", DateTime(timezone=True)),
)


# Pydantic models
class SubjectIn(BaseModel):
    TYPE_STRUCTURE: Optional[str] = None
    CODE_UKNF: Optional[str] = None
    NAME_STRUCTURE: Optional[str] = None
    LEI: Optional[str] = None
    NIP: Optional[str] = None
    KRS: Optional[str] = None
    STREET: Optional[str] = None
    NR_STRET: Optional[str] = None
    NR_HOUSE: Optional[str] = None
    POST_CODE: Optional[str] = None
    TOWN: Optional[str] = None
    PHONE: Optional[str] = None
    EMAIL: Optional[str] = None
    UKNF_ID: Optional[str] = None
    STATUS_S: Optional[str] = None
    KATEGORY_S: Optional[str] = None
    SELEKTOR_S: Optional[str] = None
    SUBSELEKTOR_S: Optional[str] = None
    TRANS_S: Optional[bool] = None


class SubjectOut(BaseModel):
    ID: int
    TYPE_STRUCTURE: Optional[str] = None
    CODE_UKNF: Optional[str] = None
    NAME_STRUCTURE: Optional[str] = None
    LEI: Optional[str] = None
    NIP: Optional[str] = None
    KRS: Optional[str] = None
    STREET: Optional[str] = None
    NR_STRET: Optional[str] = None
    NR_HOUSE: Optional[str] = None
    POST_CODE: Optional[str] = None
    TOWN: Optional[str] = None
    PHONE: Optional[str] = None
    EMAIL: Optional[str] = None
    UKNF_ID: Optional[str] = None
    STATUS_S: Optional[str] = None
    KATEGORY_S: Optional[str] = None
    SELEKTOR_S: Optional[str] = None
    SUBSELEKTOR_S: Optional[str] = None
    TRANS_S: Optional[bool] = None
    DATE_CREATE: Optional[datetime] = None
    DATE_ACTRUALIZATION: Optional[datetime] = None


class UserOut(BaseModel):
    ID: int
    USER_NAME: Optional[str] = None
    USER_LASTNAME: Optional[str] = None
    PHONE: Optional[str] = None
    EMAIL: Optional[str] = None
    PESEL: Optional[str] = None
    IS_USER_ACTIVE: Optional[bool] = None
    UKNF_ID: Optional[str] = None
    DATE_CREATE: Optional[datetime] = None
    DATE_ACTRUALIZATION: Optional[datetime] = None


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


app = FastAPI(title="Moduł Administracyjny", lifespan=lifespan)


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
    return {"status": "ok"}


@app.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    """Health check endpoint with database verification"""
    try:
        db.execute(text("SELECT 1"))
        return {"db": "up"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")


@app.post("/subjects", response_model=SubjectOut, status_code=201)
def create_subject(subject_data: SubjectIn, db: Session = Depends(get_db)):
    """Create a new subject (banking entity)"""
    # Convert Pydantic model to dict, excluding unset fields
    data = subject_data.model_dump(exclude_unset=True)
    
    # Set timestamps to current UTC time
    now = datetime.now(timezone.utc)
    data["DATE_CREATE"] = now
    data["DATE_ACTRUALIZATION"] = now
    
    # Insert and return the created row
    stmt = insert(subjects).values(**data).returning(subjects)
    result = db.execute(stmt)
    db.commit()
    
    row = result.fetchone()
    return SubjectOut(**row._mapping)


@app.get("/subjects/{id}", response_model=SubjectOut)
def get_subject(id: int, db: Session = Depends(get_db)):
    """Fetch a subject by ID"""
    stmt = select(subjects).where(subjects.c.ID == id)
    result = db.execute(stmt)
    row = result.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return SubjectOut(**row._mapping)


@app.get("/users/{id}", response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    """Fetch a user by ID"""
    stmt = select(users).where(users.c.ID == id)
    result = db.execute(stmt)
    row = result.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserOut(**row._mapping)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

