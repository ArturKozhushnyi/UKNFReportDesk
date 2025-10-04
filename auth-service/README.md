# Authentication Service

FastAPI microservice for user registration, authentication, and authorization.

## Features

- **User Registration**: Create new user accounts with email validation
- **Authentication**: Secure login with password hashing (bcrypt)
- **Authorization**: Permission checking based on user and group access
- **Session Management**: Redis-based session storage with 24-hour expiration
- **Health Checks**: Database and Redis connectivity monitoring

## Technology Stack

- Python 3.11
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Redis
- Passlib (bcrypt for password hashing)

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /authn` - Authenticate user (login)
- `POST /logout` - Logout user (invalidate session)

### Authorization
- `POST /authz` - Check user permissions for a resource

### Health & Status
- `GET /` - Service status
- `GET /healthz` - Health check with database and Redis verification

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string (default: redis://localhost:6379)

## Running the Service

### Using Docker Compose (Recommended)
```bash
docker-compose up auth-service
```

### Local Development
```bash
pip install -r requirements.txt
python main.py
```

The service will be available at `http://localhost:8001`

## API Documentation

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Database Schema

The service uses the following tables from the shared PostgreSQL schema:
- `USERS` - User accounts
- `GROUPS` - User groups
- `USERS_GROUPS` - User-group relationships
- `RESOURCES` - Available resources
- `RESOURCES_ALLOW_LIST` - Permission grants

## Security Features

- Password hashing with sha256_crypt
- Session-based authentication
- Secure session ID generation (UUID)
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy

## Security Note

While this implementation uses `sha256_crypt` for password hashing as requested, it's important to note that **`bcrypt` is generally the industry-recommended standard** for password hashing. This is because `bcrypt` is an adaptive algorithm specifically designed to be slow and resistant to hardware-accelerated (GPU) brute-force attacks, whereas SHA-256 is a general-purpose fast hash function. For production systems handling sensitive data, consider using `bcrypt` or other purpose-built password hashing algorithms like `argon2` for enhanced security.
