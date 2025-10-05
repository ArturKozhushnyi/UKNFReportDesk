import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    create_engine, text, MetaData, Table, Column,
    BigInteger, String, Boolean, DateTime, insert, select, update
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

# SUBJECTS table definition (with RESOURCE_ID for multi-tenant security)
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
    Column("VALIDATED", Boolean),
    Column("RESOURCE_ID", String(50)),  # Links to resource for access control
)

# USERS table definition (with SUBJECT_ID)
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
    Column("SUBJECT_ID", BigInteger),
    Column("DATE_CREATE", DateTime(timezone=True)),
    Column("DATE_ACTRUALIZATION", DateTime(timezone=True)),
)

# GROUPS table definition
groups = Table(
    "GROUPS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("GROUP_NAME", String(250)),
)

# USERS_GROUPS table definition
users_groups = Table(
    "USERS_GROUPS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("USER_ID", BigInteger),
    Column("GROUP_ID", BigInteger),
)

# RESOURCES table definition
resources = Table(
    "RESOURCES",
    metadata,
    Column("ID", String(50), primary_key=True),
)

# RESOURCES_ALLOW_LIST table definition
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
    subject_id: Optional[int] = None  # Optional for existing subject

class UserOut(BaseModel):
    ID: int
    USER_NAME: Optional[str] = None
    USER_LASTNAME: Optional[str] = None
    PHONE: Optional[str] = None
    EMAIL: Optional[str] = None
    PESEL: Optional[str] = None
    IS_USER_ACTIVE: Optional[bool] = None
    UKNF_ID: Optional[str] = None
    SUBJECT_ID: Optional[int] = None
    DATE_CREATE: Optional[datetime] = None
    DATE_ACTRUALIZATION: Optional[datetime] = None
    
    @staticmethod
    def mask_pesel(pesel: Optional[str]) -> Optional[str]:
        """Mask PESEL to show only last 4 digits (format: *******5123)"""
        if not pesel or len(pesel) < 4:
            return pesel
        return '*' * (len(pesel) - 4) + pesel[-4:]
    
    @classmethod
    def from_db_row(cls, row):
        """Create UserOut instance from database row with masked PESEL"""
        data = dict(row._mapping)
        if data.get('PESEL'):
            data['PESEL'] = cls.mask_pesel(data['PESEL'])
        return cls(**data)

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
    description="User registration, authentication, and authorization service with multi-tenant security",
    version="2.0.0",
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
    return {
        "status": "ok", 
        "service": "auth-service",
        "version": "2.0.0",
        "features": ["multi-tenant", "auto-admin", "subject-isolation"]
    }

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
    """
    Register a new user with automatic multi-tenant security setup.
    
    This endpoint implements a complex, atomic transaction that:
    1. Creates an isolated subject entity for the user
    2. Creates a dedicated admin resource for the subject
    3. Creates an admin group specific to the subject
    4. Grants the group permission to manage the subject
    5. Creates the user account
    6. Makes the user an admin of their own subject
    
    All operations are atomic - if any step fails, everything rolls back.
    """
    try:
        # ====================================================================
        # Step 0: Validation - Check if user already exists
        # ====================================================================
        stmt = select(users).where(users.c.EMAIL == user_data.email)
        result = db.execute(stmt)
        existing_user = result.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Generate shared UUID for user and subject
        shared_uknf_id = str(uuid.uuid4())
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Get current timestamp
        now = datetime.now(timezone.utc)
        
        # ====================================================================
        # Step 1: Create Empty Subject
        # ====================================================================
        # Create a subject entity that will be owned by this user
        subject_name = f"Subject for user {user_data.email}"
        
        subject_dict = {
            "NAME_STRUCTURE": subject_name,
            "UKNF_ID": shared_uknf_id,
            "STATUS_S": "active",
            "VALIDATED": False,
            "DATE_CREATE": now,
            "DATE_ACTRUALIZATION": now,
        }
        
        # Insert subject and capture the ID
        stmt = insert(subjects).values(**subject_dict).returning(subjects.c.ID)
        result = db.execute(stmt)
        subject_id = result.fetchone().ID
        
        print(f"[Registration] Created subject ID: {subject_id}")
        
        # ====================================================================
        # Step 2: Create Admin Resource
        # ====================================================================
        # Create a resource that represents administrative control over this subject
        resource_id = f"subject:admin:{subject_id}"
        
        stmt = insert(resources).values(ID=resource_id)
        db.execute(stmt)
        
        print(f"[Registration] Created resource: {resource_id}")
        
        # ====================================================================
        # Step 3: Link Resource to Subject
        # ====================================================================
        # Update the subject to reference its admin resource
        stmt = update(subjects).where(
            subjects.c.ID == subject_id
        ).values(RESOURCE_ID=resource_id)
        db.execute(stmt)
        
        print(f"[Registration] Linked subject {subject_id} to resource {resource_id}")
        
        # ====================================================================
        # Step 4: Create Admin Group
        # ====================================================================
        # Create a group that will have admin rights over this subject
        group_name = f"admins_of_subject_{subject_id}"
        
        stmt = insert(groups).values(GROUP_NAME=group_name).returning(groups.c.ID)
        result = db.execute(stmt)
        group_id = result.fetchone().ID
        
        print(f"[Registration] Created admin group: {group_name} (ID: {group_id})")
        
        # ====================================================================
        # Step 5: Grant Permission
        # ====================================================================
        # Link the admin group to the resource, granting it permission
        stmt = insert(resources_allow_list).values(
            RESOURCE_ID=resource_id,
            GROUP_ID=group_id,
            USER_ID=None  # Group-level permission, not user-specific
        )
        db.execute(stmt)
        
        print(f"[Registration] Granted group {group_id} permission to resource {resource_id}")
        
        # ====================================================================
        # Step 6: Create User
        # ====================================================================
        # Create the user account linked to the subject
        user_dict = {
            "EMAIL": user_data.email,
            "PASSWORD_HASH": hashed_password,
            "USER_NAME": user_data.user_name,
            "USER_LASTNAME": user_data.user_lastname,
            "PHONE": user_data.phone,
            "PESEL": user_data.pesel,
            "UKNF_ID": shared_uknf_id,
            "SUBJECT_ID": subject_id,
            "IS_USER_ACTIVE": True,
            "DATE_CREATE": now,
            "DATE_ACTRUALIZATION": now,
        }
        
        stmt = insert(users).values(**user_dict).returning(users.c.ID)
        result = db.execute(stmt)
        user_id = result.fetchone().ID
        
        print(f"[Registration] Created user ID: {user_id}")
        
        # ====================================================================
        # Step 7: Add User to Admin Group
        # ====================================================================
        # Make the user a member of the admin group for their subject
        stmt = insert(users_groups).values(
            USER_ID=user_id,
            GROUP_ID=group_id
        )
        db.execute(stmt)
        
        print(f"[Registration] Added user {user_id} to admin group {group_id}")
        
        # ====================================================================
        # Commit Transaction
        # ====================================================================
        # All operations succeeded - commit the transaction
        db.commit()
        
        print(f"[Registration] Successfully registered user {user_data.email}")
        print(f"[Registration] User is now admin of subject {subject_id}")
        
        # Return success response
        return {
            "message": "User registered successfully with admin privileges",
            "user_id": user_id,
            "subject_id": subject_id,
            "resource_id": resource_id,
            "admin_group": group_name,
            "email": user_data.email,
            "uknf_id": shared_uknf_id,
            "status": "User is now administrator of their own subject"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like duplicate email)
        raise
    except Exception as e:
        # Rollback transaction on any error
        db.rollback()
        print(f"[Registration] Error: {str(e)}")
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
