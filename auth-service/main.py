import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    create_engine, text, MetaData, Table, Column,
    BigInteger, String, Boolean, DateTime, insert, select
)
from sqlalchemy.orm import sessionmaker, Session
import redis
from passlib.context import CryptContext

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Redis setup
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Password hashing
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# Database metadata and tables
metadata = MetaData()

users = Table(
    "USERS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("USER_NAME", String(250)),
    Column("USER_LASTNAME", String(250)),
    Column("PHONE", String(250)),
    Column("EMAIL", String(500)),
    Column("PESEL", String(11)),
    Column("PASSWORD_HASH", String(128)),
    Column("IS_USER_ACTIVE", Boolean),
    Column("UKNF_ID", String(100)),
)

groups = Table(
    "GROUPS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("GROUP_NAME", String(250)),
)

users_groups = Table(
    "USERS_GROUPS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("USER_ID", BigInteger),
    Column("GROUP_ID", BigInteger),
)

resources = Table(
    "RESOURCES",
    metadata,
    Column("ID", String(50), primary_key=True),
)

resources_allow_list = Table(
    "RESOURCES_ALLOW_LIST",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("RESOURCE_ID", String(50)),
    Column("USER_ID", BigInteger),
    Column("GROUP_ID", BigInteger),
)

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    user_name: Optional[str] = None
    user_lastname: Optional[str] = None
    phone: Optional[str] = None
    pesel: Optional[str] = None
    uknf_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AuthzRequest(BaseModel):
    session_id: str
    resource_id: str

class AuthResponse(BaseModel):
    session_id: str
    expires_in: int = 86400  # 24 hours in seconds

class AuthzResponse(BaseModel):
    authorized: bool
    message: str

class ErrorResponse(BaseModel):
    detail: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup: verify database and Redis connections
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        print("Database connection verified")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise
    
    try:
        redis_client.ping()
        print("Redis connection verified")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        raise
    
    yield
    
    # Shutdown: dispose engine resources
    engine.dispose()
    redis_client.close()

app = FastAPI(
    title="Authentication Service",
    description="User registration, authentication, and authorization service",
    version="1.0.0",
    lifespan=lifespan
)

def get_db():
    """Dependency for obtaining database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

@app.get("/")
def root():
    """Root endpoint"""
    return {"status": "ok", "service": "auth-service"}

@app.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    """Health check endpoint with database and Redis verification"""
    try:
        # Check database
        db.execute(text("SELECT 1"))
        
        # Check Redis
        redis_client.ping()
        
        return {"status": "healthy", "database": "up", "redis": "up"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )

@app.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        stmt = select(users).where(users.c.EMAIL == user_data.email)
        result = db.execute(stmt)
        existing_user = result.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Prepare user data
        user_dict = {
            "EMAIL": user_data.email,
            "PASSWORD_HASH": hashed_password,
            "USER_NAME": user_data.user_name,
            "USER_LASTNAME": user_data.user_lastname,
            "PHONE": user_data.phone,
            "PESEL": user_data.pesel,
            "UKNF_ID": user_data.uknf_id,
            "IS_USER_ACTIVE": True
        }
        
        # Insert user
        stmt = insert(users).values(**user_dict).returning(users.c.ID)
        result = db.execute(stmt)
        db.commit()
        
        user_id = result.fetchone().ID
        
        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "email": user_data.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/authn", response_model=AuthResponse)
def authenticate_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and create session"""
    try:
        # Find user by email
        stmt = select(users).where(users.c.EMAIL == login_data.email)
        result = db.execute(stmt)
        user = result.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.IS_USER_ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.PASSWORD_HASH):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Store session in Redis (24 hours expiration)
        redis_client.setex(f"session:{session_id}", 86400, str(user.ID))
        
        return AuthResponse(session_id=session_id, expires_in=86400)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@app.post("/authz", response_model=AuthzResponse)
def authorize_user(authz_request: AuthzRequest, db: Session = Depends(get_db)):
    """Check if user has permission to access a resource"""
    try:
        # Validate session
        session_key = f"session:{authz_request.session_id}"
        user_id = redis_client.get(session_key)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        
        user_id = int(user_id)
        
        # Get user's groups
        stmt = select(users_groups.c.GROUP_ID).where(users_groups.c.USER_ID == user_id)
        result = db.execute(stmt)
        user_groups = [row.GROUP_ID for row in result.fetchall()]
        
        # Check permissions
        # First check direct user permissions
        stmt = select(resources_allow_list).where(
            (resources_allow_list.c.RESOURCE_ID == authz_request.resource_id) &
            (resources_allow_list.c.USER_ID == user_id)
        )
        result = db.execute(stmt)
        direct_permission = result.fetchone()
        
        if direct_permission:
            return AuthzResponse(authorized=True, message="Access granted (direct permission)")
        
        # Check group permissions
        if user_groups:
            stmt = select(resources_allow_list).where(
                (resources_allow_list.c.RESOURCE_ID == authz_request.resource_id) &
                (resources_allow_list.c.GROUP_ID.in_(user_groups))
            )
            result = db.execute(stmt)
            group_permission = result.fetchone()
            
            if group_permission:
                return AuthzResponse(authorized=True, message="Access granted (group permission)")
        
        # No permissions found
        return AuthzResponse(authorized=False, message="Access denied")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authorization check failed: {str(e)}"
        )

@app.post("/logout")
def logout_user(session_id: str):
    """Logout user by invalidating session"""
    try:
        session_key = f"session:{session_id}"
        redis_client.delete(session_key)
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
