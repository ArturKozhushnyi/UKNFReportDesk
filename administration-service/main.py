import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import (
    create_engine, text, MetaData, Table, Column,
    BigInteger, String, Boolean, DateTime, insert, select, update
)
from sqlalchemy.orm import sessionmaker, Session


# Read environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

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
    Column("VALIDATED", Boolean),
    Column("RESOURCE_ID", String(50)),
)

subjects_history = Table(
    "SUBJECTS_HISTORY",
    metadata,
    Column("HISTORY_ID", BigInteger, primary_key=True),
    Column("OPERATION_TYPE", String(10)),
    Column("MODIFIED_AT", DateTime(timezone=True)),
    Column("MODIFIED_BY", BigInteger),
    Column("ID", BigInteger),
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
    Column("PASSWORD_HASH", String(128)),
    Column("IS_USER_ACTIVE", Boolean),
    Column("UKNF_ID", String(100)),
    Column("SUBJECT_ID", BigInteger),
    Column("DATE_CREATE", DateTime(timezone=True)),
    Column("DATE_ACTRUALIZATION", DateTime(timezone=True)),
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


class SubjectUpdate(BaseModel):
    """Schema for updating subject fields"""
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
    VALIDATED: Optional[bool] = None
    RESOURCE_ID: Optional[str] = None


class SubjectHistoryOut(BaseModel):
    """Schema for subject history records"""
    HISTORY_ID: int
    OPERATION_TYPE: str
    MODIFIED_AT: datetime
    MODIFIED_BY: Optional[int] = None
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
    VALIDATED: Optional[bool] = None


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


class UserGroupAssociation(BaseModel):
    group_id: int


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


def check_authorization(resource_id: str):
    """
    Reusable authorization dependency that checks if the user has permission
    to access the specified resource by calling the auth-service.
    
    Args:
        resource_id: The resource identifier (e.g., "api:subjects:create")
    
    Returns:
        None if authorized, raises HTTPException if not authorized
    """
    def _check_auth(authorization: str = Header(None)):
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header is required"
            )
        
        # Extract Bearer token
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Authorization header must start with 'Bearer '"
            )
        
        session_id = authorization[7:]  # Remove "Bearer " prefix
        
        if not session_id:
            raise HTTPException(
                status_code=401,
                detail="Session ID is required"
            )
        
        # Call auth-service to check authorization
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{AUTH_SERVICE_URL}/authz",
                    json={
                        "session_id": session_id,
                        "resource_id": resource_id
                    },
                    timeout=5.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=403,
                        detail="Access denied: insufficient permissions"
                    )
                
                # Authorization successful
                return None
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Authorization service unavailable: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Authorization check failed: {str(e)}"
            )
    
    return _check_auth


def get_user_id_from_session(authorization: str = Header(None)) -> int:
    """
    Extract user ID from session by calling auth-service.
    
    Args:
        authorization: Bearer token with session ID
    
    Returns:
        user_id: The ID of the authenticated user
    
    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header must start with 'Bearer '"
        )
    
    session_id = authorization[7:]  # Remove "Bearer " prefix
    
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Session ID is required"
        )
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{AUTH_SERVICE_URL}/get-user-id-by-session/{session_id}",
                timeout=5.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired session"
                )
            
            data = response.json()
            return data.get("user_id")
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Authorization service unavailable: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user ID: {str(e)}"
        )


def check_subject_edit_permission(subject_id: int, authorization: str = Header(None)):
    """
    Check if the user has permission to edit a specific subject.
    User must be either a UKNF Admin or an Admin of the specific subject.
    
    Args:
        subject_id: The ID of the subject to edit
        authorization: Bearer token with session ID
    
    Returns:
        user_id: The ID of the authorized user
    
    Raises:
        HTTPException: If user doesn't have permission
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header must start with 'Bearer '"
        )
    
    session_id = authorization[7:]  # Remove "Bearer " prefix
    
    try:
        with httpx.Client() as client:
            # Check for subject-specific admin permission
            subject_resource_id = f"subject:admin:{subject_id}"
            response = client.post(
                f"{AUTH_SERVICE_URL}/authz",
                json={
                    "session_id": session_id,
                    "resource_id": subject_resource_id
                },
                timeout=5.0
            )
            
            # Check both status code AND response body
            if response.status_code == 200:
                auth_result = response.json()
                if auth_result.get("authorized") is True:
                    # User is admin of this subject, get their user ID
                    user_response = client.get(
                        f"{AUTH_SERVICE_URL}/get-user-id-by-session/{session_id}",
                        timeout=5.0
                    )
                    if user_response.status_code == 200:
                        return user_response.json().get("user_id")
            
            raise HTTPException(
                status_code=403,
                detail="Access denied: you must be an administrator of this subject to edit it"
            )
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Authorization service unavailable: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authorization check failed: {str(e)}"
        )


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
def create_subject(
    subject_data: SubjectIn, 
    db: Session = Depends(get_db),
    _: None = Depends(check_authorization("api:subjects:create"))
):
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


@app.get("/subjects/manageable", response_model=list[SubjectOut])
def get_manageable_subjects(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get a list of subjects that the current user has permission to manage.
    
    Logic:
    - If user is UKNF Admin: return all subjects
    - If user is Subject Admin: return only the subject they admin
    - If user has no admin permissions: return empty array
    """
    try:
        # Get user ID from session
        user_id = get_user_id_from_session(authorization)
        
        # Check if user is UKNF Admin by checking for administrator group
        admin_group_stmt = select(groups.c.ID).where(groups.c.GROUP_NAME == 'administrator')
        admin_group_result = db.execute(admin_group_stmt)
        admin_group_row = admin_group_result.fetchone()
        
        is_uknf_admin = False
        if admin_group_row:
            admin_group_id = admin_group_row.ID
            user_admin_stmt = select(users_groups).where(
                (users_groups.c.USER_ID == user_id) &
                (users_groups.c.GROUP_ID == admin_group_id)
            )
            user_admin_result = db.execute(user_admin_stmt)
            is_uknf_admin = user_admin_result.fetchone() is not None
        
        if is_uknf_admin:
            # User is UKNF Admin - return all subjects
            stmt = select(subjects).order_by(subjects.c.NAME_STRUCTURE.asc())
            result = db.execute(stmt)
            subjects_list = [SubjectOut(**row._mapping) for row in result.fetchall()]
            return subjects_list
        
        # Check if user is Subject Admin by looking for subject-specific admin groups
        # Pattern: "admins_of_subject_{subject_id}"
        subject_admin_stmt = (
            select(users_groups.c.GROUP_ID)
            .select_from(users_groups.join(groups, users_groups.c.GROUP_ID == groups.c.ID))
            .where(
                (users_groups.c.USER_ID == user_id) &
                (groups.c.GROUP_NAME.like('admins_of_subject_%'))
            )
        )
        subject_admin_result = db.execute(subject_admin_stmt)
        subject_admin_groups = [row.GROUP_ID for row in subject_admin_result.fetchall()]
        
        if subject_admin_groups:
            # User is admin of specific subjects - extract subject IDs from group names
            subject_ids = []
            for group_id in subject_admin_groups:
                group_name_stmt = select(groups.c.GROUP_NAME).where(groups.c.ID == group_id)
                group_name_result = db.execute(group_name_stmt)
                group_name_row = group_name_result.fetchone()
                
                if group_name_row:
                    group_name = group_name_row.GROUP_NAME
                    # Extract subject ID from "admins_of_subject_{subject_id}"
                    if group_name.startswith('admins_of_subject_'):
                        try:
                            subject_id = int(group_name.split('_')[-1])
                            subject_ids.append(subject_id)
                        except ValueError:
                            continue
            
            if subject_ids:
                # Return subjects that user can manage
                stmt = select(subjects).where(subjects.c.ID.in_(subject_ids)).order_by(subjects.c.NAME_STRUCTURE.asc())
                result = db.execute(stmt)
                subjects_list = [SubjectOut(**row._mapping) for row in result.fetchall()]
                return subjects_list
        
        # User has no admin permissions - return empty array
        return []
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve manageable subjects: {str(e)}"
        )


@app.get("/subjects/{id}", response_model=SubjectOut)
def get_subject(
    id: int, 
    db: Session = Depends(get_db),
    _: None = Depends(check_authorization("api:subjects:read"))
):
    """Fetch a subject by ID"""
    stmt = select(subjects).where(subjects.c.ID == id)
    result = db.execute(stmt)
    row = result.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return SubjectOut(**row._mapping)


@app.get("/users/{id}", response_model=UserOut)
def get_user(
    id: int, 
    db: Session = Depends(get_db),
    _: None = Depends(check_authorization("api:users:read"))
):
    """Fetch a user by ID"""
    stmt = select(users).where(users.c.ID == id)
    result = db.execute(stmt)
    row = result.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserOut.from_db_row(row)


@app.post("/users/{user_id}/groups", status_code=201)
def add_user_to_group(
    user_id: int,
    group_association: UserGroupAssociation,
    db: Session = Depends(get_db),
    _: None = Depends(check_authorization("api:users:add_to_group"))
):
    """Add a user to a group"""
    try:
        # Verify user exists
        user_stmt = select(users).where(users.c.ID == user_id)
        user_result = db.execute(user_stmt)
        user_row = user_result.fetchone()
        
        if user_row is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify group exists
        group_stmt = select(groups).where(groups.c.ID == group_association.group_id)
        group_result = db.execute(group_stmt)
        group_row = group_result.fetchone()
        
        if group_row is None:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if user is already in the group
        existing_stmt = select(users_groups).where(
            (users_groups.c.USER_ID == user_id) &
            (users_groups.c.GROUP_ID == group_association.group_id)
        )
        existing_result = db.execute(existing_stmt)
        existing_row = existing_result.fetchone()
        
        if existing_row is not None:
            raise HTTPException(
                status_code=400, 
                detail="User is already a member of this group"
            )
        
        # Add user to group
        insert_stmt = insert(users_groups).values(
            USER_ID=user_id,
            GROUP_ID=group_association.group_id
        )
        db.execute(insert_stmt)
        db.commit()
        
        return {
            "message": "User successfully added to group",
            "user_id": user_id,
            "group_id": group_association.group_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add user to group: {str(e)}"
        )


@app.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """
    Update subject information.
    Requires the user to be an administrator of the subject.
    Automatically records the change in the subjects_history table.
    """
    # Check permissions and get user ID
    user_id = check_subject_edit_permission(subject_id, authorization)
    
    try:
        # Verify subject exists
        stmt = select(subjects).where(subjects.c.ID == subject_id)
        result = db.execute(stmt)
        existing_subject = result.fetchone()
        
        if existing_subject is None:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        # Get only the fields that were provided (exclude unset fields)
        update_data = subject_data.model_dump(exclude_unset=True)
        
        if not update_data:
            # No fields to update
            return SubjectOut(**existing_subject._mapping)
        
        # Update the actualization date
        update_data["DATE_ACTRUALIZATION"] = datetime.now(timezone.utc)
        
        # Set the session variable for audit trail
        db.execute(text(f"SET LOCAL app.current_user_id = {user_id}"))
        
        # Perform the update
        update_stmt = (
            update(subjects)
            .where(subjects.c.ID == subject_id)
            .values(**update_data)
            .returning(subjects)
        )
        result = db.execute(update_stmt)
        db.commit()
        
        updated_row = result.fetchone()
        return SubjectOut(**updated_row._mapping)
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update subject: {str(e)}"
        )


@app.get("/subjects/{subject_id}/history", response_model=list[SubjectHistoryOut])
def get_subject_history(
    subject_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(check_authorization("api:subjects:read"))
):
    """
    Retrieve the change history for a specific subject.
    Returns all historical records ordered by most recent first.
    """
    try:
        # Verify subject exists
        subject_stmt = select(subjects).where(subjects.c.ID == subject_id)
        subject_result = db.execute(subject_stmt)
        subject_row = subject_result.fetchone()
        
        if subject_row is None:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        # Query history table
        history_stmt = (
            select(subjects_history)
            .where(subjects_history.c.ID == subject_id)
            .order_by(subjects_history.c.MODIFIED_AT.desc())
        )
        history_result = db.execute(history_stmt)
        history_rows = history_result.fetchall()
        
        # Convert to Pydantic models
        return [SubjectHistoryOut(**row._mapping) for row in history_rows]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve subject history: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

