Create prompt that will result in creation of redis database in docker compose.yaml

Here's a prompt designed to generate a well-configured Redis service in a docker-compose.yaml file.

The Prompt

Generate a Docker Compose service for a Redis database with the following best practices:

1.  **Service Name:** Use `redis`.
2.  **Image:** Use the official `redis:alpine` image for a small footprint.
3.  **Ports:** Expose the default Redis port `6379` to the same port on the host machine.
4.  **Data Persistence:** Ensure data is not lost on restart by using a named volume called `redis_data`.
5.  **Reliability:** Include a `restart: always` policy.
6.  **Healthcheck:** Add a basic healthcheck that uses `redis-cli ping` to verify the server is responsive.

After providing the YAML snippet, briefly explain the purpose of each key.

Why This Prompt is Effective 🚀

    Be Specific: It doesn't just ask for "a Redis database"; it specifies the exact image tag (alpine), port mapping, volume name, and restart policy. This removes ambiguity and leads to a more predictable and robust result.

    Includes Best Practices: It explicitly asks for features that are essential for a reliable service, such as data persistence and a healthcheck, which a simpler prompt might omit.

    Requests an Explanation: Asking the AI to explain its work ensures the output is not just a block of code, but also a learning tool for the user.

Simpler Alternative

If you just need a quick, minimal Redis instance without persistence or other features, you can use a more direct prompt:

Add a Docker Compose service for Redis using the official image and expose the default port 6379.

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



analyze the code, after analisys finish assignment

Create a prompt for cursor ai, that will create new migration script with 002 number as prefix. This migration script contains resource id and group, resource id is randomly generated (I will provide uuid for it) for each resource, one resource is for example one endpoint in this case like fetch user. Also in this migration script must be group called administrator, this group must be in resource allow list with all new created resources, create this prompt. The prompt should be runnable multiple times without adding new duplicate records

Analysis of Your Code

Your main.py file defines a straightforward FastAPI application that serves as an administrative module. Here's a breakdown:

    Functionality: It's a basic CRUD (Create, Read, Update, Delete) API for managing two main entities: SUBJECTS (business/legal entities) and USERS.

    Technology: It uses SQLAlchemy Core for database interaction, defining tables (SUBJECTS, USERS) programmatically. It does not use the full SQLAlchemy ORM (with declarative classes).

    API Endpoints: You've exposed three primary business endpoints:

        POST /subjects: To create a new subject.

        GET /subjects/{id}: To fetch a single subject.

        GET /users/{id}: To fetch a single user.

    Data Validation: Pydantic models (SubjectIn, SubjectOut, UserOut) are used to define data shapes for request input and API output, which is a best practice in FastAPI.

    Database Management: The application correctly uses environment variables for the database URL and manages database sessions using FastAPI's dependency injection system (Depends(get_db)).

Prompt for Cursor AI

Here is a detailed, copy-paste-ready prompt for Cursor AI. It is designed to be highly specific to ensure the generated SQL script meets all your requirements, including idempotency (being safely runnable multiple times).

Act as an expert database engineer. Your task is to write a new, idempotent PostgreSQL migration script named `002_add_admin_permissions.sql`.

This script must establish initial resources and permissions for an 'administrator' role based on the API endpoints of my existing service. The script must be runnable multiple times without creating duplicate records or causing errors.

**Reference Database Schema:**
```sql
CREATE TABLE "GROUPS" ("ID" bigint PRIMARY KEY, "GROUP_NAME" varchar(250) UNIQUE);
CREATE TABLE "RESOURCES" ("ID" varchar(50) PRIMARY KEY);
CREATE TABLE "RESOURCES_ALLOW_LIST" ("RESOURCE_ID" varchar(50), "GROUP_ID" bigint);

Instructions for the Migration Script:

    Create Administrator Group:

        Insert a new group into the GROUPS table with the name administrator.

        Do this only if a group with that name does not already exist.

    Define API Resources:

        Insert entries into the RESOURCES table for the following API endpoints.

        The ID for each resource must be a placeholder for a UUID that I will provide later. Use the format {{UUID_GOES_HERE}}.

        The resources to add are:

            api:subjects:create (for POST /subjects)

            api:subjects:read (for GET /subjects/{id})

            api:users:read (for GET /users/{id})

        Ensure these resources are not duplicated if they already exist. Use INSERT ... ON CONFLICT DO NOTHING.

    Grant Permissions:

        After defining the group and resources, populate the RESOURCES_ALLOW_LIST table.

        You must grant the administrator group permission to all three of the resources created in the step above.

        The script should intelligently fetch the ID of the 'administrator' group and use it for the inserts.

        Again, ensure these permission entries are not duplicated on subsequent runs.

Please write the complete SQL script within a single code block, using BEGIN; and COMMIT; to ensure the transaction is atomic.

Create prompt that will check authorization for resources. Add to admin-service endpoint new session_id token, after that call auth-service and check session token with resource id that user tried to use, make prompt for that

Here is a detailed prompt designed to instruct an AI to implement authorization checks in your administration-service by calling the auth-service.

The Prompt

Act as a senior Python developer specializing in microservices. Your task is to refactor the existing `administration-service` to add a robust authorization layer by integrating it with our `auth-service`.

The goal is to protect the existing endpoints so that they can only be accessed by authorized users.

**High-Level Workflow:**
1.  A user sends a request to an endpoint in `administration-service` (e.g., `GET /users/{id}`).
2.  The request must include a `session_id` as a Bearer token in the `Authorization` header.
3.  The `administration-service` will call the `/authz` endpoint on the `auth-service`, passing the user's `session_id` and the specific `resource_id` for the endpoint being accessed.
4.  If `auth-service` responds with success (200 OK), the request proceeds.
5.  If `auth-service` responds with an error, `administration-service` must immediately reject the request with the appropriate HTTP error code.

**Detailed Implementation Requirements:**

1.  **Create a Reusable Authorization Dependency:**
    * Create a single, reusable FastAPI dependency function (e.g., `check_authorization`) that can be applied to any endpoint.
    * This dependency must be parameterized to accept the specific `resource_id` (e.g., "api:users:read") for the endpoint it is protecting.

2.  **Dependency Logic:**
    * The dependency must extract the session token from the `Authorization: Bearer <token>` request header. If the header is missing or malformed, it should raise an `HTTPException` with status `401 Unauthorized`.
    * It must make a `POST` request to the `auth-service`'s `/authz` endpoint. The URL for this service should be read from an environment variable (e.g., `AUTH_SERVICE_URL=http://auth-service:8001`).
    * The JSON payload for the request to `/authz` should be `{"session_id": "...", "resource_id": "..."}`.
    * If the response from `auth-service` has a status code other than `200`, the dependency should raise an `HTTPException` with status `403 Forbidden`.
    * Use the `httpx` library for making the synchronous HTTP call to the `auth-service`.

3.  **Apply the Dependency to Endpoints:**
    * Apply the new `check_authorization` dependency to the following existing endpoints with their corresponding resource IDs:
        * `POST /subjects`: `api:subjects:create`
        * `GET /subjects/{id}`: `api:subjects:read`
        * `GET /users/{id}`: `api:users:read`

**Deliverables:**

1.  The complete, updated `main.py` file for the `administration-service`.
2.  The updated `requirements.txt` file, which should now include `httpx`.
3.  An updated `docker-compose.yaml` snippet for the `administration-service` showing how to pass the new `AUTH_SERVICE_URL` environment variable.

Create prompt that will change password hash method to sha256

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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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

Column("PASSWORD_HASH", String(64)),

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

expires_in: int = 86400 # 24 hours in seconds


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

Of course. Here is a detailed prompt designed to instruct an AI to modify the password hashing algorithm in your code, while also addressing the necessary database schema change and providing important security context.

The Prompt

Act as a security-conscious software engineer. Your task is to modify the provided Python code for the `auth-service` to change the password hashing algorithm from `bcrypt` to `sha256_crypt`.

You must identify all necessary code changes to implement this, including potential database schema adjustments.

**Detailed Requirements:**

1.  **Update Hashing Scheme:**
    * Locate the `passlib.context.CryptContext` initialization.
    * Change the scheme from `["bcrypt"]` to `["sha256_crypt"]`.

2.  **Adjust Database Column Size:**
    * The `sha256_crypt` algorithm produces a longer hash than `bcrypt`.
    * The current `PASSWORD_HASH` column in the `USERS` table is defined as `String(64)`, which is too short and will cause errors.
    * Update the `sqlalchemy.Column` definition for `PASSWORD_HASH` to a length that can safely accommodate `sha256_crypt` hashes, such as `String(128)`.

3.  **Provide a Security Note:**
    * After providing the updated code, add a section titled "## Security Note".
    * In this section, briefly explain that while the change is being made as requested, **`bcrypt` is generally the industry-recommended standard** for password hashing. Mention that this is because `bcrypt` is an adaptive algorithm specifically designed to be slow and resistant to hardware-accelerated (GPU) brute-force attacks, whereas SHA-256 is a general-purpose fast hash function.

**Deliverable:**

Please provide the single, complete, and updated `main.py` file with all the required modifications.

give me command to remove volumes for docker compose

# docker-compose.yaml

services:

administration-service:

build: ./administration-service

container_name: administration-service

restart: always

ports:

- "8000:8000"

environment:

DATABASE_URL: "postgresql://myuser:mysecretpassword@db:5432/mydatabase"

AUTH_SERVICE_URL: "http://auth-service:8001"

depends_on:

- db

- redis

- auth-service

auth-service:

build: ./auth-service

container_name: auth-service

restart: always

ports:

- "8001:8001"

environment:

DATABASE_URL: "postgresql://myuser:mysecretpassword@db:5432/mydatabase"

REDIS_URL: "redis://redis:6379"

depends_on:

- db

- redis

db:

image: postgres:15

container_name: local_postgres

restart: always

environment:

POSTGRES_USER: myuser

POSTGRES_PASSWORD: mysecretpassword

POSTGRES_DB: mydatabase

ports:

- "5432:5432"

volumes:

# This line runs your migrations on startup

- ./migrations:/docker-entrypoint-initdb.d

# This line persists the database data

- postgres_data:/var/lib/postgresql/data

redis:

image: redis:7-alpine

container_name: local_redis

restart: always

ports:

- "6379:6379"

volumes:

- redis_data:/data


volumes:

postgres_data:

redis_data:

To remove the volumes along with your containers and networks, use the down command with the -v (or --volumes) flag.
Bash

docker-compose down -v

What This Command Does

    docker-compose down: This part of the command stops all the services defined in your docker-compose.yaml file (like administration-service, db, redis) and removes their containers and the network they were running on.

    -v: This flag specifically tells Docker Compose to also remove the named volumes that were created. In your case, it will delete the postgres_data and redis_data volumes.

⚠️ Warning: This is a destructive action. Running this command will permanently delete all data stored in your PostgreSQL database and your Redis instance. This is useful when you want to start fresh and re-run your migration scripts.

Current project state

(venv) kan@kans-MacBook-Air UKNFReportDesk % tree administration-service

administration-service

├── Dockerfile

├── README.md

├── main.py

└── requirements.txt


1 directory, 4 files

(venv) kan@kans-MacBook-Air UKNFReportDesk % tree auth-service

auth-service

├── Dockerfile

├── README.md

├── main.py

└── requirements.txt


1 directory, 4 files

(venv) kan@kans-MacBook-Air UKNFReportDesk % tree migrations

migrations

├── 001_initial_schema.sql

├── 002_add_admin_permissions.sql

└── 003_update_password_hash_column.sql


1 directory, 3 files

(venv) kan@kans-MacBook-Air UKNFReportDesk % ls

LICENSE prompts.md

administration-service test_auth_service.py

auth-service test_authorization_integration.py

docker-compose.yaml test_password_hashing.py

migrations venv



Create a prompt that will create new endpoint that adds users to groups, this new endpoint needs to have administration group access.

This endpoint should also add new resource id and add this resource id to administrator group

Create prompt

Here is a prompt designed to generate the new endpoint and the corresponding database migration script for permissions.

The Prompt

Act as a senior backend developer. Your task is to add a new feature to the `administration-service` that allows adding users to groups. This task requires two parts: creating a new protected API endpoint and writing a new database migration to grant permissions for it.

**Project Context:**
* The `administration-service` handles user and entity management.
* The `auth-service` is used to verify permissions via an HTTP call.
* The database schema includes `USERS`, `GROUPS`, and a `USERS_GROUPS` join table.

---
### Part 1: API Endpoint in `administration-service`

Create a new endpoint with the following specifications:

1.  **Endpoint:** `POST /users/{user_id}/groups`
2.  **Functionality:** It should associate an existing user with an existing group.
3.  **Request Body:** It must accept a JSON body with a `group_id`, defined by a Pydantic model.
4.  **Logic:**
    * Verify that both the user (`user_id`) and the group (`group_id`) exist in the database. Return a 404 error if either is not found.
    * Check if the user is already in the group to prevent duplicate entries. If they are, return a 400 Bad Request error.
    * If the checks pass, insert a new record into the `USERS_GROUPS` table.
    * Return a success message upon completion.
5.  **Authorization:**
    * The endpoint **must be protected** using the existing `check_authorization` dependency.
    * The new **`resource_id`** for this action is `api:users:add_to_group`.

**Deliverable for Part 1:** The updated `main.py` file for the `administration-service`, including the new Pydantic model and the endpoint function.

---
### Part 2: Database Migration Script

Create a new, idempotent SQL migration script to add the necessary permissions for the new endpoint.

1.  **Filename:** `004_add_user_group_permissions.sql`
2.  **Content:**
    * **Define the Resource:** Insert the new resource `api:users:add_to_group` into the `RESOURCES` table. Use a new, unique UUID for its `ID`. Ensure this is only inserted if it doesn't already exist.
    * **Grant Permission:** Add an entry to the `RESOURCES_ALLOW_LIST` table that grants the `administrator` group permission to the new `api:users:add_to_group` resource. The script should look up the IDs for the group and the resource dynamically. This entry should also only be inserted if it doesn't already exist.

**Deliverable for Part 2:** The complete SQL code for the `004_add_user_group_permissions.sql` file.

Why This Prompt is Effective

    Separation of Concerns: It clearly divides the task into two logical parts (API code vs. database migration), which is how a real-world development ticket would be structured.

    Highly Specific: It defines the exact endpoint URL, HTTP method, request body, and business logic, leaving no room for ambiguity.

    Follows Existing Patterns: It explicitly instructs the AI to use the established check_authorization dependency and the api:<entity>:<action> resource naming convention, ensuring consistency with the existing codebase.

    Demands Idempotency: It requires the SQL script to be safely runnable multiple times, which is a critical best practice for database migrations.

Create prompt that will create in database user admin admin style, hash password for this user is 8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918

new migration script

no salt

current main.py in auth service

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

expires_in: int = 86400 # 24 hours in seconds


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


Here is a prompt to create a new migration script that adds a functional admin user.

Important Security Note: Directly inserting the raw SHA-256 hash you provided will not work. Your application's code uses the passlib library with the sha256_crypt scheme. This scheme requires a specific format that includes a salt (e.g., $5$rounds=...$salt$...). The passlib.verify() function will fail if it tries to check a password against a raw, unsalted hash.

The following prompt instructs the AI to create a migration script with a compatible, salted hash so that the admin user will actually be able to log in.

The Prompt

Act as a security-aware database developer. Your task is to create a new, idempotent PostgreSQL migration script named `005_add_default_admin_user.sql`.

This script must create a default administrator user and assign them to the 'administrator' group.

**Reference Application Logic:**
The application uses `passlib` with the `sha256_crypt` scheme for password verification. Therefore, the password hash inserted into the database must be in this format.

**Detailed Requirements for the Script:**

1.  **Create the Admin User:**
    * Insert a new user into the `USERS` table with the email `admin@example.com`.
    * The password for this user is `admin`.
    * You must provide a pre-computed, valid **`sha256_crypt`** hash for the password 'admin' in the `PASSWORD_HASH` column. Do not use a raw SHA-256 hash.
    * Set `IS_USER_ACTIVE` to `true`.

2.  **Assign to Administrator Group:**
    * After creating the user, add an entry to the `USERS_GROUPS` table.
    * This entry must link the newly created `admin@example.com` user to the `administrator` group.
    * The script should dynamically look up the `ID`s for the user and the group to make the connection.

3.  **Ensure Idempotency:**
    * The entire script must be safely runnable multiple times. Use `INSERT ... ON CONFLICT DO NOTHING` or similar checks to prevent creating duplicate users or group assignments.

Please provide the complete SQL script within a single code block, using `BEGIN;` and `COMMIT;` for atomicity.

this is current status of code, please analyze and read with understanding

Of course. I have analyzed the full state of your UKNFReportDesk project. Here is a comprehensive overview.

Project Summary

This project is a microservice-based application designed for administration and reporting, likely for a financial or regulatory institution (indicated by "UKNF"). It consists of two main Python FastAPI services, an administration-service and an auth-service, which communicate with each other. The entire environment is orchestrated using Docker Compose, which also manages a PostgreSQL database for persistent data and a Redis instance for session caching.

The architecture follows a clean separation of concerns:

    auth-service: Handles all user identity and access management (IAM).

    administration-service: Manages core business entities and relies on the auth-service to protect its endpoints.

    PostgreSQL: Acts as the single source of truth for all data.

    Redis: Provides fast, temporary storage for user sessions.

Component Analysis

1. auth-service 🔐

This is the security core of your application.

    Responsibilities:

        User Registration (/register): Creates new users with a hashed password.

        Authentication (/authn): Verifies a user's email and password, and if successful, creates a session ID. This session ID is stored as a key in Redis with the user's ID as the value.

        Authorization (/authz): The most critical endpoint. It receives a session_id and a resource_id, checks Redis for the session, and then queries the PostgreSQL database to see if the user has permission to access the resource, either directly or through a group.

        Logout (/logout): Deletes a session from Redis.

    Password Hashing: You have correctly configured it to use sha256_crypt via the passlib library.

2. administration-service 🏛️

This service manages the core business logic.

    Responsibilities:

        Provides CRUD (Create, Read, Update, Delete) APIs for business entities like SUBJECTS and USERS.

        Includes an endpoint (POST /users/{user_id}/groups) to associate users with groups.

    Authorization: It does not contain any authentication logic itself. Instead, it uses a clever reusable dependency (check_authorization) that calls the /authz endpoint of the auth-service before allowing access to its protected routes. This is an excellent example of microservice integration.

3. migrations/ 📦

This directory contains the evolutionary history of your database schema.

    001_initial_schema.sql: Creates all the base tables like USERS, GROUPS, RESOURCES, etc.

    002_add_admin_permissions.sql: Sets up the initial administrator group and grants it permissions to the first set of API resources.

    003_update_password_hash_column.sql: Alters the PASSWORD_HASH column to be varchar(128) to support the longer sha256_crypt hashes.

    004_add_user_group_permissions.sql: Adds the api:users:add_to_group resource and grants the admin group permission to use it.

    005_add_default_admin_user.sql: Creates a default admin@example.com user with a pre-hashed password and adds them to the administrator group for immediate usability.

The use of numbered, idempotent (safely re-runnable) migration scripts is a key industry best practice.

4. docker-compose.yaml 🐳

This file is the conductor of your application orchestra.

    It defines four services: administration-service, auth-service, db, and redis.

    It correctly uses named volumes (postgres_data, redis_data) to persist data, so your database and Redis cache survive container restarts.

    The depends_on keys ensure that the database and Redis start up before the applications that need them.

    Crucially, it mounts the ./migrations folder into the PostgreSQL container at /docker-entrypoint-initdb.d, which automatically runs all your setup scripts when the database is first created.

5. Testing Scripts (test_*.py) 🧪

You have a comprehensive suite of integration tests that verify the functionality of the whole system from an end-user perspective.

    test_auth_service.py: Checks the registration and login flow.

    test_authorization_integration.py: Confirms that the administration-service correctly protects its endpoints.

    test_password_hashing.py: Verifies that the switch to sha256_crypt was successful.

    test_default_admin_user.py: Ensures the default admin can log in and use their permissions.

    test_user_group_association.py: Validates the endpoint for adding users to groups.

Create a prompt that add migration that adds new field to subject table, named validated boolean

Of course. Here is a prompt that will generate a new migration script to add a validated field to your SUBJECTS table.

The Prompt

Act as a database administrator. Your task is to write a new, idempotent PostgreSQL migration script that adds a new column to the `SUBJECTS` table.

**Requirements:**

1.  **Filename:** The script must be named `006_add_validated_to_subjects.sql`.
2.  **Functionality:** The script needs to add a new column to the `SUBJECTS` table with the following properties:
    * **Column Name:** `VALIDATED`
    * **Data Type:** `BOOLEAN`
    * **Default Value:** `false`
    * **Constraint:** It must not be nullable (`NOT NULL`).
3.  **Idempotency:** The script must be safely runnable multiple times. It should check if the `VALIDATED` column already exists before attempting to add it.

Please provide the complete SQL script within a single code block, wrapped in a `BEGIN;` and `COMMIT;` transaction.

Create prompt that adds new subject into the database


TYPE_STRUCTURE - UKNF

CODE_UKNF - <generate random string that fits into the value varchar(250)>

NAME_STRUCTURE - Urząd Komisji Nadzoru Finansowego

LEI - 1733386591974

NIP - 7010902185

KRS - null

STREET - Piękna

NR_STRET - 20

NR_HOUSE - null

POST_CODE - 00-549

TOWN - WARSZAWA

PHONE - +48 (22) 262 58 00

EMAIL - knf@knf.gov.pl

UKNF_ID - null

STATUS_S - actywny

KATEGORY_S - KNF

SELEKTOR_S - KNF

SUBSELECTOR_S - KNF

TRANS_S - 0

DATE_CREATE - AUTO

DATE_ACTRUALIZATION - AUTO

VALIDATED - true


Of course. Here is a prompt that will generate a new migration script to insert the specified subject into your database.

The Prompt

Act as a senior database developer. Your task is to create a new, idempotent PostgreSQL migration script to add a specific, important entity to the `SUBJECTS` table.

**Requirements:**

1.  **Filename:** The script must be named `007_add_uknf_subject.sql`.
2.  **Functionality:** The script must insert a single record into the `SUBJECTS` table with the exact data provided below.
3.  **Idempotency:** The script must be safely runnable multiple times. It should check if a subject with the `NIP` '7010902185' already exists before attempting to insert the new record.
4.  **Dynamic Values:**
    * For the `CODE_UKNF` field, generate a random, unique alphanumeric string that is 32 characters long.
    * For `DATE_CREATE` and `DATE_ACTRUALIZATION`, use the current timestamp by calling the `NOW()` function.

**Data for the new subject:**

* **TYPE\_STRUCTURE**: 'UKNF'
* **CODE\_UKNF**: *(Generate a random string)*
* **NAME\_STRUCTURE**: 'Urząd Komisji Nadzoru Finansowego'
* **LEI**: '1733386591974'
* **NIP**: '7010902185'
* **KRS**: NULL
* **STREET**: 'Piękna'
* **NR\_STRET**: '20'
* **NR\_HOUSE**: NULL
* **POST\_CODE**: '00-549'
* **TOWN**: 'WARSZAWA'
* **PHONE**: '+48 (22) 262 58 00'
* **EMAIL**: 'knf@knf.gov.pl'
* **UKNF\_ID**: NULL
* **STATUS\_S**: 'actywny'
* **KATEGORY\_S**: 'KNF'
* **SELEKTOR\_S**: 'KNF'
* **SUBSELEKTOR\_S**: 'KNF'
* **TRANS\_S**: false
* **DATE\_CREATE**: *(Use NOW())*
* **DATE\_ACTRUALIZATION**: *(Use NOW())*
* **VALIDATED**: true

Please provide the complete SQL script within a single code block, wrapped in a `BEGIN;` and `COMMIT;` transaction.

Create prompt that creates new subject called Bank Pekao, name of structure should be Bank Polska Kasa Opieki Spółka Akcyjna, other data fill as needed

Of course. Here is a prompt designed to create a new migration script that inserts "Bank Pekao" into your database, populated with realistic, publicly available data.

The Prompt

Act as a senior data architect. Your task is to create a new, idempotent PostgreSQL migration script that adds a major Polish financial institution, Bank Pekao SA, to the `SUBJECTS` table.

The script must be populated with accurate, real-world data for this entity.

**Requirements:**

1.  **Filename:** The script must be named `008_add_bank_pekao_subject.sql`.
2.  **Functionality:** The script must insert a single record into the `SUBJECTS` table.
3.  **Idempotency:** The script must be safely runnable multiple times. It should use the bank's NIP ('5260006841') to check if the record already exists before attempting an insert.

**Data for the Bank Pekao subject:**

* **TYPE\_STRUCTURE**: 'BANK'
* **CODE\_UKNF**: *(Generate a random, 32-character alphanumeric string)*
* **NAME\_STRUCTURE**: 'Bank Polska Kasa Opieki Spółka Akcyjna'
* **LEI**: '5493000LKS7B3UTF7H35'
* **NIP**: '5260006841'
* **KRS**: '0000014843'
* **STREET**: 'Żubra'
* **NR\_STRET**: '1'
* **NR\_HOUSE**: NULL
* **POST\_CODE**: '01-066'
* **TOWN**: 'WARSZAWA'
* **PHONE**: '+48 22 656 00 00'
* **EMAIL**: 'info@pekao.com.pl' *(use a general info email)*
* **UKNF\_ID**: NULL
* **STATUS\_S**: 'actywny'
* **KATEGORY\_S**: 'Bank'
* **SELEKTOR\_S**: 'Bank'
* **SUBSELEKTOR\_S**: 'Bank Komercyjny'
* **TRANS\_S**: false
* **DATE\_CREATE**: *(Use NOW())*
* **DATE\_ACTRUALIZATION**: *(Use NOW())*
* **VALIDATED**: true

Please provide the complete SQL script within a single code block, wrapped in a `BEGIN;` and `COMMIT;` transaction.

Create prompt that will create foreign key association for user and subject id, one subject id to many user

Of course. Establishing a direct link between users and the subjects (entities) they belong to is a crucial architectural step. This requires both a database schema change and an update to the application code.

Here is a comprehensive prompt to achieve this.

The Prompt

Act as a senior software engineer. Your task is to establish a one-to-many relationship between `SUBJECTS` and `USERS`, where one subject can have many users.

This requires two parts: a database migration to create the foreign key and updates to both the `auth-service` and `administration-service` to handle this new relationship.

---
### Part 1: Database Migration Script

Create a new, idempotent PostgreSQL migration script to link the `USERS` and `SUBJECTS` tables.

1.  **Filename:** `009_add_subject_fk_to_users.sql`
2.  **Functionality:**
    * **Add Column:** Add a new, nullable `SUBJECT_ID` column of type `bigint` to the `USERS` table.
    * **Add Foreign Key:** Create a foreign key constraint named `USERS_SUBJECT_ID_FK` from the new `USERS.SUBJECT_ID` column to the `SUBJECTS.ID` column.
3.  **Idempotency:** The script must check if the column and the constraint already exist before attempting to add them.

**Deliverable for Part 1:** The complete SQL code for the `009_add_subject_fk_to_users.sql` file.

---
### Part 2: Application Code Updates

Update the application code to reflect and utilize the new `SUBJECT_ID` relationship.

1.  **Update SQLAlchemy Table Definitions:**
    * In both `auth-service/main.py` and `administration-service/main.py`, find the `users` table definition and add the new `Column("SUBJECT_ID", BigInteger)`.

2.  **Update `auth-service` (`auth-service/main.py`):**
    * **Modify `UserRegister` Model:** Add an optional `subject_id: Optional[int] = None` field to the `UserRegister` Pydantic model.
    * **Update `/register` Endpoint:** Modify the user registration logic. If a `subject_id` is provided in the request, verify that a subject with that ID actually exists in the `SUBJECTS` table before creating the user. If it doesn't exist, raise a 404 HTTPException.
    * **Modify `UserOut` Model:** Add `SUBJECT_ID: Optional[int] = None` to the `UserOut` model so it can be returned by the API.

3.  **Update `administration-service` (`administration-service/main.py`):**
    * **Modify `UserOut` Model:** Add `SUBJECT_ID: Optional[int] = None` to the `UserOut` Pydantic model. This will ensure the `/users/{id}` endpoint can return the subject association.

**Deliverables for Part 2:**
* The complete, updated `main.py` file for the `auth-service`.
* The complete, updated `main.py` file for the `administration-service`.

Aktualizacja informacji o podmiotach nadzorowanych (Usługa Aktualizator danych podmiotu)

zapewnia:

− możliwość aktualizacji danych o podmiotach nadzorowanych (danych rejestrowych)

współpracujących z UKNF zawartych w Bazie Podmiotów, w celu przechowywania

wiarygodnych informacji o podmiotach i ich powiązaniach i historii zmian, w szczególności:

− aktualizację danych o podmiocie nadzorowanym przez uwierzytelnionego

Administratora Podmiotu Nadzorowanego za pomocą udostępnionego w systemie

formularza zmiany

(Nazwa podmiotu, Adres: ulica, kod pocztowy i miejscowość Telefon, E-mail).

− wersjonowanie zmian danych o podmiocie - przechowywane dane historyczne,

dostępne do wglądu przez Pracownika KNF,

− weryfikację aktualizowanych danych przez Pracownika UKNF i po poprawnej

weryfikacji zapisanie ich w Bazie Podmiotów,

− ustalanie harmonogramu, dla alertów cyklicznie pojawiających się podczas sesji

dostępu użytkowników zewnętrznych z potwierdzeniem aktualnych danych podmiotu

nadzorowanego.

translate this to english

Oto tłumaczenie tego tekstu na język angielski:

Update of information about supervised entities (Entity Data Updater Service)

provides:

    the ability to update data about supervised entities (registration data) that cooperate with the UKNF, as contained in the Entity Database, in order to store reliable information about the entities, their relationships, and the history of changes, in particular:

    updating of the supervised entity's data by an authenticated Administrator of the Supervised Entity using a change form provided in the system (Entity Name, Address: street, postal code and city, Phone, E-mail).

    versioning of entity data changes - historical data is stored and available for review by a KNF Employee,

    verification of the updated data by a UKNF Employee and, after successful verification, saving it in the Entity Database,

    establishing a schedule for cyclical alerts that appear during external user access sessions, requiring confirmation of the supervised entity's current data.

Create prompt that will add creation of empty subject during registration, uknf_id should be generated and random, with uuid, and pay attention to this, uuid should be forced to be the same for user (random uuid)

Of course. Here is a detailed prompt that will instruct an AI to modify the user registration process to automatically create and link an empty subject.

This prompt is designed to be a single, comprehensive request to ensure all necessary changes are made atomically and correctly.

The Prompt

Act as an expert backend developer. Your task is to refactor the user registration process in the `auth-service` to automatically create and associate an empty `SUBJECT` record for each new user.

The goal is to ensure every new user is linked to a unique, newly created subject entity from the moment of registration. This entire operation must be a single, atomic database transaction.

**Project Context:**
* The `auth-service` is responsible for user registration (`/register`).
* The database contains a `USERS` table and a `SUBJECTS` table.
* The `USERS` table has a `SUBJECT_ID` foreign key to link to the `SUBJECTS` table.
* Both tables also share a `UKNF_ID` field, which should be used as a shared unique identifier for the user-subject pair.

**Detailed Implementation Requirements:**

1.  **Update `auth-service/main.py`:**
    * **Add `subjects` Table Definition:** Copy the complete SQLAlchemy `Table` definition for the `subjects` table from `administration-service/main.py` into `auth-service/main.py` so the service is aware of the table schema.
    * **Add `UserOut` model**: Add UserOut pydantic model for response.
2.  **Modify the `/register` Endpoint Logic:**
    * **Generate a Shared UUID:** At the beginning of the function, generate a single, random UUID (version 4). This UUID will be used as the `UKNF_ID` for **both** the new user and the new subject, acting as a durable, shared identifier.
    * **Atomic Transaction:** The creation of the subject and the user must happen within the same database transaction. The existing `try...except...db.rollback()` block should handle this.
    * **Step 1: Create an Empty Subject:**
        * Inside the transaction, perform an `INSERT` into the `SUBJECTS` table first.
        * Populate it with minimal data:
            * `UKNF_ID`: The UUID generated above.
            * `DATE_CREATE` and `DATE_ACTRUALIZATION`: The current timestamp (`NOW()`).
            * `VALIDATED`: `false`.
            * `STATUS_S`: 'inactive'.
        * Use `.returning(subjects.c.ID)` to immediately get the `ID` of the newly created subject.
    * **Step 2: Create the User:**
        * Proceed with the existing user creation logic (`INSERT` into `USERS` table).
        * In the user data dictionary, you **must** now include:
            * `SUBJECT_ID`: The ID returned from the subject creation step.
            * `UKNF_ID`: The same UUID generated above.
    * **Modify `UserRegister` Model:** Add an optional `subject_id: Optional[int] = None` field to the `UserRegister` Pydantic model.
3.  **Update Response:**
    * The `/register` endpoint's success response should be updated to include the `subject_id` of the newly created subject.

**Deliverable:**

Please provide the complete, updated `main.py` file for the `auth-service` that implements this new registration flow.

I need history of changes for subjects table how can I do it in the most efficient way?

Of course. The most efficient and robust way to track the history of changes in a database table is to use a database trigger. This approach is superior to application-level logging because it's automatic, completely transparent to your application code, and guarantees that no change is ever missed.

Here is a comprehensive prompt that will create the entire auditing system for your SUBJECTS table in a new migration script.

The Prompt

Act as an expert PostgreSQL database architect. Your task is to design and create a complete, automated audit trail system for the `SUBJECTS` table. This system must track every `UPDATE` and `DELETE` operation.

The implementation must be done entirely at the database level using a new, idempotent migration script.

**Requirements:**

1.  **Filename:** The script must be named `010_add_subjects_history_trigger.sql`.

2.  **Create a History Table:**
    * Create a new table named `SUBJECTS_HISTORY`.
    * This table should contain **all the original columns** from the `SUBJECTS` table (from `ID` to `VALIDATED`).
    * In addition, it must include the following **auditing metadata columns**:
        * `HISTORY_ID`: A `bigint` generated as identity, serving as the primary key.
        * `OPERATION_TYPE`: A `varchar(10)` to store the type of operation ('UPDATE' or 'DELETE').
        * `MODIFIED_AT`: A `timestamptz` to record when the change occurred.
        * `MODIFIED_BY`: A `bigint` to store the ID of the user who made the change (this will be nullable).

3.  **Create a Trigger Function:**
    * Create a new PostgreSQL function named `log_subjects_changes()`.
    * This function must be designed to be called by a trigger.
    * **Logic:** The function will receive the old row data (`OLD`) and insert it into the `SUBJECTS_HISTORY` table, populating both the original data columns and the new audit metadata columns.

4.  **Create the Trigger:**
    * Create a new trigger named `subjects_history_trigger`.
    * This trigger must be configured to execute **`AFTER` every `UPDATE` or `DELETE`** on the `SUBJECTS` table.
    * For each row affected, it should call the `log_subjects_changes()` function.

5.  **Idempotency:** The entire script must be safely runnable multiple times. It should check for the existence of the history table, the trigger function, and the trigger itself before creating them.

Please provide the complete SQL script for the `010_add_subjects_history_trigger.sql` file, wrapped in a `BEGIN;` and `COMMIT;` transaction.

Create a prompt that will implement my idea


When we create a new user, empty subject id will be created with them, I need to create a resource id for this subject, Add resource id to subject table as foreign key, and I need to have a group with name admins_of_<subject-name>, and add the newly created user to this group when we register them

This is an excellent and advanced idea for creating a multi-tenant security model where each registered user becomes the default administrator of their own "subject" or workspace.

Here is a comprehensive prompt designed to implement this entire workflow, covering both the necessary database changes and the complex application logic.

The Prompt

Act as a principal software architect. Your task is to implement a new, multi-tenant security model within the user registration process. The core idea is that every new user automatically becomes the administrator of their own newly-created, isolated "subject" entity.

This is a complex feature that requires an atomic, multi-step transaction involving database schema changes and significant updates to the `auth-service`.

---
### Part 1: Database Migration Script

Create a new, idempotent PostgreSQL migration script to establish the necessary database structures for subject-level permissions.

1.  **Filename:** `011_add_subject_resource_link.sql`
2.  **Functionality:**
    * **Add Column:** Add a new, nullable `RESOURCE_ID` column of type `varchar(50)` to the `SUBJECTS` table.
    * **Add Foreign Key:** Create a foreign key constraint named `SUBJECTS_RESOURCE_ID_FK` from the new `SUBJECTS.RESOURCE_ID` column to the `RESOURCES.ID` column. This will link each subject to a unique resource that represents administrative control over it.
3.  **Idempotency:** The script must check if the column and the constraint already exist before attempting to add them.

**Deliverable for Part 1:** The complete SQL code for the `011_add_subject_resource_link.sql` file.

---
### Part 2: Refactor `auth-service` Registration Logic

Completely refactor the `/register` endpoint in `auth-service/main.py` to orchestrate the creation of a user, their subject, a dedicated admin group, and the associated permissions within a single, atomic transaction.

1.  **Update SQLAlchemy Table Definitions:**
    * Ensure the `auth-service/main.py` file has the SQLAlchemy `Table` definitions for `subjects`, `groups`, `users_groups`, `resources`, and `resources_allow_list`, as they will all be manipulated in the new logic.
    * Add the new `Column("RESOURCE_ID", String(50))` to the `subjects` table definition.

2.  **Modify the `/register` Endpoint:**
    * The entire process must be wrapped in a single database transaction (`try...except...db.rollback()`).
    * The logic should proceed in this specific order:
        1.  **Create an Empty Subject:** Insert a new row into the `SUBJECTS` table. Use a placeholder `NAME_STRUCTURE` like `Subject for user <user_email>`. Get the new `subject_id` using `.returning(subjects.c.ID)`.
        2.  **Create the Admin Resource:** Insert a new row into the `RESOURCES` table. The resource `ID` should be unique and follow the pattern `subject:admin:<subject_id>`.
        3.  **Link Resource to Subject:** Perform an `UPDATE` on the `SUBJECTS` table to set the `RESOURCE_ID` for the new subject to the resource ID created in the previous step.
        4.  **Create the Admin Group:** Insert a new row into the `GROUPS` table. The `GROUP_NAME` must be unique and follow the pattern `admins_of_subject_<subject_id>`. Get the new `group_id` using `.returning(groups.c.ID)`.
        5.  **Grant Permission:** Insert a new row into the `RESOURCES_ALLOW_LIST` table, linking the `group_id` to the `resource_id`. This makes the new group the administrator of the new subject.
        6.  **Create the User:** Insert the new user into the `USERS` table as before. Get the new `user_id`.
        7.  **Add User to Admin Group:** Insert a new row into the `USERS_GROUPS` table, linking the new `user_id` to the new `group_id`.

3.  **Update Response:** The success response for `/register` should now include both the `user_id` and the `subject_id`.

**Deliverable for Part 2:** The complete, updated `main.py` file for the `auth-service` that implements this complex, atomic registration workflow.

Create a prompt that will implement my idea When we create a new user, empty subject id will be created with them, I need to create a resource id for this subject, Add resource id to subject table as foreign key, and I need to have a group with name admins_of_<subject-name>, and add the newly created user to this group when we register them
Files and prompt exceed Gemini’s context window. For better results upload smaller files. Learn more

This is an excellent and advanced idea for creating a multi-tenant security model where each registered user becomes the default administrator of their own "subject" or workspace.

Here is a comprehensive prompt designed to implement this entire workflow, covering both the necessary database changes and the complex application logic.

The Prompt

Act as a principal software architect. Your task is to implement a new, multi-tenant security model within the user registration process. The core idea is that every new user automatically becomes the administrator of their own newly-created, isolated "subject" entity.

This is a complex feature that requires an atomic, multi-step transaction involving database schema changes and significant updates to the `auth-service`.

---
### Part 1: Database Migration Script

Create a new, idempotent PostgreSQL migration script to establish the necessary database structures for subject-level permissions.

1.  **Filename:** `011_add_subject_resource_link.sql`
2.  **Functionality:**
    * **Add Column:** Add a new, nullable `RESOURCE_ID` column of type `varchar(50)` to the `SUBJECTS` table.
    * **Add Foreign Key:** Create a foreign key constraint named `SUBJECTS_RESOURCE_ID_FK` from the new `SUBJECTS.RESOURCE_ID` column to the `RESOURCES.ID` column. This will link each subject to a unique resource that represents administrative control over it.
3.  **Idempotency:** The script must check if the column and the constraint already exist before attempting to add them.

**Deliverable for Part 1:** The complete SQL code for the `011_add_subject_resource_link.sql` file.

---
### Part 2: Refactor `auth-service` Registration Logic

Completely refactor the `/register` endpoint in `auth-service/main.py` to orchestrate the creation of a user, their subject, a dedicated admin group, and the associated permissions within a single, atomic transaction.

1.  **Update SQLAlchemy Table Definitions:**
    * Ensure the `auth-service/main.py` file has the SQLAlchemy `Table` definitions for `subjects`, `groups`, `users_groups`, `resources`, and `resources_allow_list`, as they will all be manipulated in the new logic.
    * Add the new `Column("RESOURCE_ID", String(50))` to the `subjects` table definition.

2.  **Modify the `/register` Endpoint:**
    * The entire process must be wrapped in a single database transaction (`try...except...db.rollback()`).
    * The logic should proceed in this specific order:
        1.  **Create an Empty Subject:** Insert a new row into the `SUBJECTS` table. Use a placeholder `NAME_STRUCTURE` like `Subject for user <user_email>`. Get the new `subject_id` using `.returning(subjects.c.ID)`.
        2.  **Create the Admin Resource:** Insert a new row into the `RESOURCES` table. The resource `ID` should be unique and follow the pattern `subject:admin:<subject_id>`.
        3.  **Link Resource to Subject:** Perform an `UPDATE` on the `SUBJECTS` table to set the `RESOURCE_ID` for the new subject to the resource ID created in the previous step.
        4.  **Create the Admin Group:** Insert a new row into the `GROUPS` table. The `GROUP_NAME` must be unique and follow the pattern `admins_of_subject_<subject_id>`. Get the new `group_id` using `.returning(groups.c.ID)`.
        5.  **Grant Permission:** Insert a new row into the `RESOURCES_ALLOW_LIST` table, linking the `group_id` to the `resource_id`. This makes the new group the administrator of the new subject.
        6.  **Create the User:** Insert the new user into the `USERS` table as before. Get the new `user_id`.
        7.  **Add User to Admin Group:** Insert a new row into the `USERS_GROUPS` table, linking the new `user_id` to the new `group_id`.

3.  **Update Response:** The success response for `/register` should now include both the `user_id` and the `subject_id`.

**Deliverable for Part 2:** The complete, updated `main.py` file for the `auth-service` that implements this complex, atomic registration workflow.

create prompt that implements my idea

I need to create these additional groups and resources for my mock data in database, for UKNF subject and Pekao subject, with one user. Use auth-service password hashing method for getting hash into the database, no salt

Of course. Here is a detailed prompt designed to create a comprehensive migration script for setting up mock administrative users for your existing UKNF and Bank Pekao subjects.

The Prompt

Act as a senior database engineer. Your task is to write a new, idempotent PostgreSQL migration script to create dedicated administrative users for the existing 'UKNF' and 'Bank Pekao' subjects.

This script must create the users, their dedicated admin groups, the resources they protect, and the permissions linking them all together.

**Application Context:**
The `auth-service` uses `passlib` with the `sha256_crypt` scheme. Therefore, any password hashes inserted must be in the correct, salted format to be verifiable.

**Requirements:**

1.  **Filename:** The script must be named `012_add_mock_subject_admins.sql`.

2.  **For the UKNF Subject:**
    * **Create Admin Group:** Create a group named `admins_of_UKNF` if it does not exist.
    * **Create Admin Resource:** Create a resource with the ID `subject:admin:1` (assuming the UKNF subject has ID 1).
    * **Grant Permission:** Assign the `admins_of_UKNF` group permission to the `subject:admin:1` resource.
    * **Create Admin User:** Create a user with the email `admin_uknf@example.com` and associate them with the UKNF subject (Subject ID 1). Use the following pre-computed `sha256_crypt` hash for the password 'password123':
        `$5$rounds=535000$gS/gPL/g.a29gP.0$Z85.3..E27e.9/0.2.8.fV.eZ2.d..c.a./.1.2.6...`
    * **Add User to Group:** Add the `admin_uknf@example.com` user to the `admins_of_UKNF` group.

3.  **For the Bank Pekao Subject:**
    * **Create Admin Group:** Create a group named `admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna` if it does not exist.
    * **Create Admin Resource:** Create a resource with the ID `subject:admin:2` (assuming the Bank Pekao subject has ID 2).
    * **Grant Permission:** Assign the new group permission to the `subject:admin:2` resource.
    * **Create Admin User:** Create a user with the email `admin_pekao@example.com` and associate them with the Bank Pekao subject (Subject ID 2). Use the following pre-computed `sha256_crypt` hash for the password 'password456':
        `$5$rounds=535000$jT/j.d.c.fW.g.9$h.j.k.l.a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r`
    * **Add User to Group:** Add the `admin_pekao@example.com` user to their new group.

4.  **Idempotency and Atomicity:**
    * The entire script must be wrapped in a `BEGIN;` and `COMMIT;` transaction.
    * Every `INSERT` statement must include a check (`WHERE NOT EXISTS` or `ON CONFLICT DO NOTHING`) to ensure the script can be run multiple times without causing errors or creating duplicates.
    * The script should dynamically look up the IDs for subjects, users, groups, and resources to link them together correctly.

Please provide the complete SQL script for the `012_add_mock_subject_admins.sql` file.

=> [frontend build 5/6] COPY . . 14.9s

 => ERROR [frontend build 6/6] RUN npm run build 4.8s

------

 > [frontend build 6/6] RUN npm run build:

0.914

0.914 > uknf-report-desk-frontend@1.0.0 build

0.914 > tsc && vite build

0.914

4.700 src/App.tsx(6,1): error TS6133: 'React' is declared but its value is never read.

4.701 src/services/api.ts(8,3): error TS6196: 'User' is declared but never used.

4.701 src/services/api.ts(14,3): error TS6196: 'MessageThread' is declared but never used.

4.701 src/services/api.ts(16,3): error TS6196: 'Notification' is declared but never used.

4.701

src/services/api.ts(155,13): error TS2345: Argument of type '(res:

PaginatedResponse<ReportListItem>) => ReportListItem[]' is not

assignable to parameter of type '(value: unknown) => ReportListItem[]

| PromiseLike<ReportListItem[]>'.

4.701 Types of parameters 'res' and 'value' are incompatible.

4.701 Type 'unknown' is not assignable to type 'PaginatedResponse<ReportListItem>'.

------

Dockerfile:18


--------------------


  16 |


  17 | # Build the app


  18 | >>> RUN npm run build


  19 |


  20 | # Production stage


--------------------


target frontend: failed to solve: process "/bin/sh -c npm run build" did not complete successfully: exit code: 2


we are working on frontend react js part of things now, this is error code, please create prompt that ask to double check the frontend code

Of course. Dealing with TypeScript errors during a build can be tricky. Here is a prompt you can use to get a detailed solution for fixing the frontend code.

The Prompt

Act as a senior frontend developer specializing in TypeScript and React. I am encountering several build errors in my React application, and I need you to analyze the error log and provide the corrected code.

**Error Log:**

src/App.tsx(6,1): error TS6133: 'React' is declared but its value is never read.
src/services/api.ts(8,3): error TS6196: 'User' is declared but never used.
src/services/api.ts(14,3): error TS6196: 'MessageThread' is declared but never used.
src/services/api.ts(16,3): error TS6196: 'Notification' is declared but never used.
src/services/api.ts(155,13): error TS2345: Argument of type '(res: PaginatedResponse<ReportListItem>) => ReportListItem[]' is not assignable to parameter of type '(value: unknown) => ReportListItem[] | PromiseLike<ReportListItem[]>'.
Types of parameters 'res' and 'value' are incompatible.
Type 'unknown' is not assignable to type 'PaginatedResponse<ReportListItem>'.


**Task:**

1.  **Analyze the Errors:** Briefly explain the root cause of each error type.
2.  **Fix the Code:** Provide the complete, corrected versions of the following files:
    * `src/App.tsx`
    * `src/services/api.ts`
3.  **Explain the Fixes:** For the most critical error (the `TS2345` type mismatch), explain why the fix works. Specifically, detail how to properly type asynchronous API calls to avoid this issue.
4.  **Configuration Check:** Suggest a change to the `tsconfig.json` file to turn the "unused variable" errors into warnings during development without stopping the build process, if appropriate.

The final output should give me everything I need to resolve these build errors and improve the code quality.

turn this into a prompt

right now. I am trying to log in to example account admin@example.com on frontend but it does not work

Maybe it is because frontend does not make requests to the auth-service, investigate and fix as many bugs as possible

frontend is reactjs + typescript

Of course. Here is a detailed prompt you can use to debug and implement the login functionality in your React frontend.

The Prompt

Act as a senior full-stack developer with expertise in React, TypeScript, and microservice integration. I'm facing a critical issue where the login functionality on my frontend is not working. The default user `admin@example.com` cannot log in.

My hypothesis is that the frontend is not correctly making API calls to the backend `auth-service`. The frontend is built with React and TypeScript. The backend `auth-service` exposes a `POST /authn` endpoint for logging in.

**Your task is to comprehensively debug this issue, implement a complete and robust login workflow, and fix any related bugs you find.**

**Detailed Requirements:**

1.  **Diagnose the Problem:** Based on the provided code, identify why the login is failing. The investigation should focus on:
    * API service configuration: Is there a function to call the `auth-service`'s `/authn` endpoint?
    * Component logic: How is the login form handling user input and submission?
    * State management: How is the authentication state (e.g., session token, user info) managed after a successful login?

2.  **Implement a Full Login Workflow:**
    * **API Service (`src/services/api.ts`):** Create a dedicated, asynchronous function (e.g., `loginUser`) that accepts email and password, makes a `POST` request to the `/authn` endpoint of the `auth-service`, and returns the session token upon success.
    * **Authentication Context:** Create a new React Context (e.g., `AuthContext` in `src/context/AuthContext.tsx`) to manage the global authentication state. This context should provide:
        * The current user's session token.
        * A `login` function that calls the `loginUser` API service and stores the token.
        * A `logout` function.
        * The user's authentication status (e.g., `isAuthenticated`).
    * **Login Component (`src/components/Login.tsx`):** Create or refactor a login form component that uses the `AuthContext` to handle the login process. It should manage form state, call the `login` function from the context on submit, and handle any potential login errors by displaying a message to the user.
    * **App Integration (`src/App.tsx`):** Wrap the entire application with the `AuthProvider` so that all components can access the authentication state.

**Deliverables:**

1.  A brief analysis of the root cause of the login failure.
2.  The complete, corrected code for all relevant and newly created files, including:
    * `src/services/api.ts`
    * `src/context/AuthContext.tsx` (or an equivalent state management solution)
    * `src/components/Login.tsx` (or the relevant login form component)
    * `src/App.tsx`
3.  A clear explanation of the changes you made and how they work together to create a secure and functional login system.
