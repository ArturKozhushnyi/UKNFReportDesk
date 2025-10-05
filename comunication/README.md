# Communication Service

FastAPI microservice for chat and messaging functionality in the UKNF Report Desk system.

## Features

- **Conversations**: Create and manage support conversations/tickets
- **Messages**: Send public and internal messages with threading support
- **Participants**: Multi-party conversations with role-based access
- **Tags**: Organize conversations with flexible tagging
- **Attachments**: File attachments for messages
- **Read Receipts**: Track message read status
- **Reactions**: Emoji reactions to messages
- **Assignment**: Conversation assignment and history tracking

## Installation

### Local Development

```bash
pip install -r requirements.txt
```

### Docker

```bash
docker build -t communication-service .
docker run -p 8002:8002 \
  -e DATABASE_URL="postgresql://user:password@localhost:5432/dbname" \
  -e AUTH_SERVICE_URL="http://auth-service:8001" \
  communication-service
```

## Database Setup

The service uses the shared PostgreSQL database. Migrations are located in the project root `migrations/` directory.

Apply migration 009_chat_schema.sql:

```bash
psql -U your_user -d your_database -f ../migrations/009_chat_schema.sql
```

## Environment Variables

- `DATABASE_URL` (required): PostgreSQL connection string
- `AUTH_SERVICE_URL` (optional): Auth service URL for authorization (default: http://auth-service:8001)

## Running

### Local

```bash
python main.py
```

### With uvicorn directly

```bash
uvicorn main:app --reload --port 8002
```

## API Documentation

Available after startup at:
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

## Endpoints

### Base URL: `/api/chat`

#### Conversations
- `POST /conversations` - Create conversation
- `GET /conversations` - List conversations (with filtering)
- `GET /conversations/{id}` - Get conversation details
- `PATCH /conversations/{id}` - Update conversation
- `GET /conversations/{id}/assignments` - Get assignment history
- `POST /conversations/{id}/assignments` - Assign conversation

#### Messages
- `POST /conversations/{id}/messages` - Send message
- `GET /conversations/{id}/messages` - List messages
- `GET /messages/{id}` - Get single message
- `PATCH /messages/{id}` - Edit message
- `DELETE /messages/{id}` - Delete message (soft)

#### Participants
- `GET /conversations/{id}/participants` - List participants
- `POST /conversations/{id}/participants` - Add participant
- `DELETE /conversations/{id}/participants/{user_id}` - Remove participant

#### Tags
- `GET /conversations/{id}/tags` - List tags
- `POST /conversations/{id}/tags` - Add tag
- `DELETE /conversations/{id}/tags/{tag}` - Remove tag

#### Attachments
- `POST /messages/{id}/attachments` - Add attachment
- `GET /messages/{id}/attachments` - List attachments

#### Read Receipts
- `POST /messages/{id}/read` - Mark as read
- `GET /messages/{id}/reads` - List read receipts
- `GET /conversations/{id}/unread-count` - Get unread count
- `GET /unread-summary` - Get unread summary

#### Reactions
- `GET /messages/{id}/reactions` - List reactions
- `POST /messages/{id}/reactions` - Add reaction
- `DELETE /messages/{id}/reactions` - Remove reaction

## Architecture

```
comunication/
├── app/
│   ├── __init__.py
│   ├── database.py           # Database table definitions
│   ├── routers/
│   │   ├── __init__.py
│   │   └── chat.py           # Chat endpoints (32 endpoints)
│   └── schemas/
│       ├── __init__.py
│       └── chat.py           # Pydantic models (22 schemas)
├── Dockerfile
├── main.py                   # FastAPI application
├── README.md
└── requirements.txt
```

## Database Tables

The service interacts with these tables:
- `CONVERSATIONS` - Main conversation records
- `CONVERSATION_PARTICIPANTS` - Participants in conversations
- `MESSAGES` - Individual messages
- `MESSAGE_ATTACHMENTS` - File attachments
- `READ_RECEIPTS` - Message read tracking
- `MESSAGE_REACTIONS` - Emoji reactions
- `CONVERSATION_TAGS` - Conversation tags
- `ASSIGNMENT_HISTORY` - Assignment tracking

References:
- `SUBJECTS` - Banking entities (from administration-service)
- `USERS` - System users (from auth-service)

## Development

### Project Structure

- `main.py` - FastAPI application entry point
- `app/routers/chat.py` - All chat endpoints (~1,300 lines)
- `app/schemas/chat.py` - Pydantic request/response models (~350 lines)
- `app/database.py` - SQLAlchemy table definitions (~140 lines)

### Code Quality

- Type hints throughout
- Comprehensive docstrings
- OpenAPI documentation
- Error handling
- Transaction management

## Testing

Run tests (when implemented):

```bash
pytest
```

## Related Services

- **auth-service** (port 8001): Authentication and authorization
- **administration-service** (port 8000): Administration and user management
- **PostgreSQL** (port 5432): Shared database
- **Redis** (port 6379): Session storage (used by auth-service)

## Documentation

See project documentation:
- `CHAT_API_DOCUMENTATION.md` - Complete API reference
- `CHAT_SYSTEM.md` - Database schema and usage patterns
- `CHAT_SYSTEM_SUMMARY.md` - System overview
- `CHAT_IMPLEMENTATION_SUMMARY.md` - Implementation details

## License

See LICENSE file in project root (GNU General Public License v2.0)

