# Chat API Documentation

## Overview

Comprehensive REST API for the chat/messaging system. All endpoints are available under `/api/chat` prefix.

**Base URL:** `http://localhost:8000/api/chat`  
**OpenAPI Docs:** `http://localhost:8000/docs`

---

## Table of Contents

- [Conversation Endpoints](#conversation-endpoints)
- [Message Endpoints](#message-endpoints)
- [Participant Endpoints](#participant-endpoints)
- [Tag Endpoints](#tag-endpoints)
- [Attachment Endpoints](#attachment-endpoints)
- [Read Receipt Endpoints](#read-receipt-endpoints)
- [Reaction Endpoints](#reaction-endpoints)
- [Assignment Endpoints](#assignment-endpoints)

---

## Conversation Endpoints

### POST /api/chat/conversations

Create a new conversation/ticket.

**Request Body:**
```json
{
  "subject_id": 1,
  "type": "support",
  "title": "Cannot submit monthly report",
  "priority": "high",
  "created_by_user_id": 5,
  "assigned_to_user_id": 3,
  "participants": [
    {"user_id": 5, "role": "requester"},
    {"user_id": 3, "role": "agent"}
  ],
  "tags": ["urgent", "technical-issue"]
}
```

**Enum Values:**
- `type`: support, inquiry, complaint, consultation, report
- `priority`: low, normal, high, urgent, critical
- `role`: requester, agent, observer, manager

**Response:** `201 Created`
```json
{
  "ID": 1,
  "SUBJECT_ID": 1,
  "TYPE": "support",
  "STATUS": "open",
  "PRIORITY": "high",
  "TITLE": "Cannot submit monthly report",
  "CREATED_BY_USER_ID": 5,
  "ASSIGNED_TO_USER_ID": 3,
  "CREATED_AT": "2025-10-05T10:00:00Z",
  "UPDATED_AT": "2025-10-05T10:00:00Z",
  "CLOSED_AT": null,
  "LAST_MESSAGE_AT": null,
  "METADATA": null,
  "participants": [...],
  "tags": ["urgent", "technical-issue"]
}
```

---

### GET /api/chat/conversations

List conversations with filtering and pagination.

**Query Parameters:**
- `subject_id` (int, optional) - Filter by subject
- `status` (string, optional) - Filter by status
- `priority` (string, optional) - Filter by priority
- `assigned_to_user_id` (int, optional) - Filter by assignee
- `tag` (string, optional) - Filter by tag
- `q` (string, optional) - Search in title
- `page` (int, default: 1) - Page number
- `page_size` (int, default: 20, max: 100) - Items per page
- `sort` (string, default: "last_message_at_desc") - Sort order

**Sort Options:**
- `last_message_at_desc` - Most recent messages first
- `created_at_desc` - Newest conversations first
- `priority` - By priority level

**Example:**
```
GET /api/chat/conversations?status=open&priority=high&page=1&page_size=20
```

**Response:** `200 OK`
```json
{
  "items": [...],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

### GET /api/chat/conversations/{conversation_id}

Get conversation details with participants and tags.

**Response:** `200 OK`
```json
{
  "ID": 1,
  "SUBJECT_ID": 1,
  "TYPE": "support",
  "STATUS": "open",
  "PRIORITY": "high",
  "TITLE": "Cannot submit monthly report",
  "CREATED_BY_USER_ID": 5,
  "ASSIGNED_TO_USER_ID": 3,
  "CREATED_AT": "2025-10-05T10:00:00Z",
  "UPDATED_AT": "2025-10-05T10:00:00Z",
  "CLOSED_AT": null,
  "LAST_MESSAGE_AT": "2025-10-05T10:15:00Z",
  "METADATA": null,
  "participants": [
    {
      "ID": 1,
      "CONVERSATION_ID": 1,
      "USER_ID": 5,
      "ROLE": "requester",
      "JOINED_AT": "2025-10-05T10:00:00Z",
      "LEFT_AT": null,
      "IS_ACTIVE": true
    }
  ],
  "tags": ["urgent", "technical-issue"]
}
```

---

### PATCH /api/chat/conversations/{conversation_id}

Update conversation fields.

**Query Parameter:**
- `current_user_id` (int, required) - User making the change

**Request Body:**
```json
{
  "status": "resolved",
  "priority": "normal",
  "assigned_to_user_id": 7
}
```

**Enum Values:**
- `status`: open, pending, resolved, closed, archived
- `priority`: low, normal, high, urgent, critical

**Response:** `200 OK`
```json
{
  "ID": 1,
  "STATUS": "resolved",
  "PRIORITY": "normal",
  "ASSIGNED_TO_USER_ID": 7,
  ...
}
```

**Note:** Changing `assigned_to_user_id` automatically creates an assignment history record.

---

## Message Endpoints

### POST /api/chat/conversations/{conversation_id}/messages

Send a message in a conversation.

**Request Body:**
```json
{
  "sender_user_id": 5,
  "body": "I cannot access the report submission form.",
  "visibility": "public",
  "message_type": "message",
  "parent_message_id": null
}
```

**Enum Values:**
- `visibility`: public, internal
- `message_type`: message, note, system, notification

**Response:** `201 Created`
```json
{
  "ID": 10,
  "CONVERSATION_ID": 1,
  "SENDER_USER_ID": 5,
  "PARENT_MESSAGE_ID": null,
  "BODY": "I cannot access the report submission form.",
  "VISIBILITY": "public",
  "MESSAGE_TYPE": "message",
  "CREATED_AT": "2025-10-05T10:15:00Z",
  "UPDATED_AT": null,
  "DELETED_AT": null,
  "IS_EDITED": false,
  "METADATA": null
}
```

**Note:** This endpoint automatically updates `LAST_MESSAGE_AT` on the conversation.

---

### GET /api/chat/conversations/{conversation_id}/messages

List messages in a conversation.

**Query Parameters:**
- `before_id` (int, optional) - Get messages before this ID (cursor pagination)
- `after_id` (int, optional) - Get messages after this ID
- `limit` (int, default: 50, max: 100) - Number of messages
- `visibility` (string, optional) - Filter by visibility
- `is_staff` (bool, default: false) - Whether user is staff (sees internal messages)

**Example:**
```
GET /api/chat/conversations/1/messages?limit=50&is_staff=true
```

**Response:** `200 OK`
```json
{
  "items": [
    {
      "ID": 10,
      "CONVERSATION_ID": 1,
      "SENDER_USER_ID": 5,
      "BODY": "I cannot access the report submission form.",
      "VISIBILITY": "public",
      "MESSAGE_TYPE": "message",
      "CREATED_AT": "2025-10-05T10:15:00Z",
      "IS_EDITED": false
    }
  ],
  "total": 1,
  "has_more": false
}
```

**Visibility Rules:**
- Non-staff users only see `public` messages
- Staff users see both `public` and `internal` messages

---

### GET /api/chat/messages/{message_id}

Get a single message by ID.

**Response:** `200 OK`
```json
{
  "ID": 10,
  "CONVERSATION_ID": 1,
  "SENDER_USER_ID": 5,
  "BODY": "I cannot access the report submission form.",
  "VISIBILITY": "public",
  "CREATED_AT": "2025-10-05T10:15:00Z",
  ...
}
```

---

### PATCH /api/chat/messages/{message_id}

Edit a message.

**Request Body:**
```json
{
  "body": "I cannot access the report submission form. Error code: ERR_403",
  "visibility": "public"
}
```

**Response:** `200 OK`
```json
{
  "ID": 10,
  "BODY": "I cannot access the report submission form. Error code: ERR_403",
  "IS_EDITED": true,
  "UPDATED_AT": "2025-10-05T10:20:00Z",
  ...
}
```

**Note:** Sets `IS_EDITED=true` and updates `UPDATED_AT`.

---

### DELETE /api/chat/messages/{message_id}

Soft delete a message.

**Response:** `204 No Content`

**Note:** Sets `DELETED_AT` timestamp. Message is not physically removed.

---

## Participant Endpoints

### GET /api/chat/conversations/{conversation_id}/participants

List all participants in a conversation.

**Response:** `200 OK`
```json
[
  {
    "ID": 1,
    "CONVERSATION_ID": 1,
    "USER_ID": 5,
    "ROLE": "requester",
    "JOINED_AT": "2025-10-05T10:00:00Z",
    "LEFT_AT": null,
    "IS_ACTIVE": true
  },
  {
    "ID": 2,
    "CONVERSATION_ID": 1,
    "USER_ID": 3,
    "ROLE": "agent",
    "JOINED_AT": "2025-10-05T10:00:00Z",
    "LEFT_AT": null,
    "IS_ACTIVE": true
  }
]
```

---

### POST /api/chat/conversations/{conversation_id}/participants

Add a participant to a conversation.

**Request Body:**
```json
{
  "user_id": 7,
  "role": "observer"
}
```

**Response:** `201 Created`
```json
{
  "ID": 3,
  "CONVERSATION_ID": 1,
  "USER_ID": 7,
  "ROLE": "observer",
  "JOINED_AT": "2025-10-05T10:30:00Z",
  "LEFT_AT": null,
  "IS_ACTIVE": true
}
```

**Note:** Idempotent - if participant already exists, returns existing record.

---

### DELETE /api/chat/conversations/{conversation_id}/participants/{user_id}

Remove a participant from a conversation.

**Response:** `204 No Content`

**Note:** Sets `IS_ACTIVE=false` and `LEFT_AT` timestamp.

---

## Tag Endpoints

### GET /api/chat/conversations/{conversation_id}/tags

List all tags for a conversation.

**Response:** `200 OK`
```json
[
  {
    "ID": 1,
    "CONVERSATION_ID": 1,
    "TAG": "urgent",
    "ADDED_BY_USER_ID": 3,
    "ADDED_AT": "2025-10-05T10:00:00Z"
  },
  {
    "ID": 2,
    "CONVERSATION_ID": 1,
    "TAG": "technical-issue",
    "ADDED_BY_USER_ID": 3,
    "ADDED_AT": "2025-10-05T10:00:00Z"
  }
]
```

---

### POST /api/chat/conversations/{conversation_id}/tags

Add a tag to a conversation.

**Request Body:**
```json
{
  "tag": "vip",
  "added_by_user_id": 3
}
```

**Tag Format:**
- Lowercase letters, numbers, hyphens, underscores only
- Pattern: `^[a-z0-9\-_]+$`

**Common Tags:**
- `vip` - VIP customer
- `urgent` - Urgent attention needed
- `sla-breach-risk` - At risk of SLA breach
- `technical-issue` - Technical problem
- `billing` - Billing related
- `escalated` - Escalated to management

**Response:** `201 Created`
```json
{
  "ID": 3,
  "CONVERSATION_ID": 1,
  "TAG": "vip",
  "ADDED_BY_USER_ID": 3,
  "ADDED_AT": "2025-10-05T10:35:00Z"
}
```

---

### DELETE /api/chat/conversations/{conversation_id}/tags/{tag}

Remove a tag from a conversation.

**Response:** `204 No Content`

---

## Attachment Endpoints

### POST /api/chat/messages/{message_id}/attachments

Add a file attachment to a message.

**Request Body:**
```json
{
  "file_name": "report_error_screenshot.png",
  "file_path": "/uploads/2025/10/abc123.png",
  "file_size": 245678,
  "mime_type": "image/png",
  "uploaded_by_user_id": 5
}
```

**Constraints:**
- `file_size`: 1 byte to 100MB (104,857,600 bytes)
- `file_name`: 1-500 characters
- `file_path`: 1-1000 characters

**Response:** `201 Created`
```json
{
  "ID": 1,
  "MESSAGE_ID": 10,
  "FILE_NAME": "report_error_screenshot.png",
  "FILE_PATH": "/uploads/2025/10/abc123.png",
  "FILE_SIZE": 245678,
  "MIME_TYPE": "image/png",
  "UPLOADED_BY_USER_ID": 5,
  "UPLOADED_AT": "2025-10-05T10:40:00Z",
  "METADATA": null
}
```

---

### GET /api/chat/messages/{message_id}/attachments

List all attachments for a message.

**Response:** `200 OK`
```json
[
  {
    "ID": 1,
    "MESSAGE_ID": 10,
    "FILE_NAME": "report_error_screenshot.png",
    "FILE_PATH": "/uploads/2025/10/abc123.png",
    "FILE_SIZE": 245678,
    "MIME_TYPE": "image/png",
    "UPLOADED_BY_USER_ID": 5,
    "UPLOADED_AT": "2025-10-05T10:40:00Z",
    "METADATA": null
  }
]
```

---

## Read Receipt Endpoints

### POST /api/chat/messages/{message_id}/read

Mark a message as read by a user.

**Request Body:**
```json
{
  "user_id": 3,
  "read_at": "2025-10-05T10:45:00Z"
}
```

**Response:** `204 No Content`

**Note:** Idempotent - safe to call multiple times for the same user/message.

---

### GET /api/chat/messages/{message_id}/reads

Get all users who have read a message.

**Response:** `200 OK`
```json
[
  {
    "ID": 1,
    "MESSAGE_ID": 10,
    "USER_ID": 3,
    "READ_AT": "2025-10-05T10:45:00Z"
  },
  {
    "ID": 2,
    "MESSAGE_ID": 10,
    "USER_ID": 7,
    "READ_AT": "2025-10-05T10:46:00Z"
  }
]
```

---

### GET /api/chat/conversations/{conversation_id}/unread-count

Get unread message count for a user in a conversation.

**Query Parameter:**
- `user_id` (int, required) - User ID

**Example:**
```
GET /api/chat/conversations/1/unread-count?user_id=5
```

**Response:** `200 OK`
```json
{
  "conversation_id": 1,
  "unread_count": 3
}
```

---

### GET /api/chat/unread-summary

Get unread counts across all conversations for a user.

**Query Parameter:**
- `user_id` (int, required) - User ID

**Example:**
```
GET /api/chat/unread-summary?user_id=5
```

**Response:** `200 OK`
```json
{
  "items": [
    {
      "conversation_id": 1,
      "unread_count": 3
    },
    {
      "conversation_id": 5,
      "unread_count": 1
    }
  ],
  "total_unread": 4
}
```

---

## Reaction Endpoints

### GET /api/chat/messages/{message_id}/reactions

Get aggregated reactions for a message.

**Response:** `200 OK`
```json
[
  {
    "emoji": "👍",
    "count": 3,
    "user_ids": [3, 5, 7]
  },
  {
    "emoji": "❤️",
    "count": 1,
    "user_ids": [5]
  }
]
```

---

### POST /api/chat/messages/{message_id}/reactions

Add an emoji reaction to a message.

**Request Body:**
```json
{
  "user_id": 3,
  "emoji": "👍"
}
```

**Response:** `204 No Content`

**Note:** Idempotent - safe to call multiple times for the same user/emoji/message.

---

### DELETE /api/chat/messages/{message_id}/reactions

Remove an emoji reaction from a message.

**Request Body:**
```json
{
  "user_id": 3,
  "emoji": "👍"
}
```

**Response:** `204 No Content`

---

## Assignment Endpoints

### GET /api/chat/conversations/{conversation_id}/assignments

Get assignment history for a conversation.

**Response:** `200 OK`
```json
[
  {
    "ID": 2,
    "CONVERSATION_ID": 1,
    "ASSIGNED_FROM_USER_ID": 3,
    "ASSIGNED_TO_USER_ID": 7,
    "ASSIGNED_BY_USER_ID": 2,
    "ASSIGNED_AT": "2025-10-05T11:00:00Z",
    "NOTE": "Escalated to senior agent"
  },
  {
    "ID": 1,
    "CONVERSATION_ID": 1,
    "ASSIGNED_FROM_USER_ID": null,
    "ASSIGNED_TO_USER_ID": 3,
    "ASSIGNED_BY_USER_ID": 5,
    "ASSIGNED_AT": "2025-10-05T10:00:00Z",
    "NOTE": "Initial assignment"
  }
]
```

**Note:** Ordered by `ASSIGNED_AT` descending (most recent first).

---

### POST /api/chat/conversations/{conversation_id}/assignments

Assign or reassign a conversation to a user.

**Query Parameter:**
- `current_user_id` (int, required) - User making the assignment

**Request Body:**
```json
{
  "assigned_to_user_id": 7,
  "note": "Escalated to senior agent for complex technical issue"
}
```

**Response:** `200 OK`
```json
{
  "ID": 1,
  "ASSIGNED_TO_USER_ID": 7,
  "UPDATED_AT": "2025-10-05T11:00:00Z",
  ...
}
```

**Note:** Automatically creates an assignment history record.

---

## Error Responses

### 400 Bad Request
Invalid input data or enum values.

```json
{
  "detail": "Invalid enum value for type, status, or priority"
}
```

### 404 Not Found
Resource not found.

```json
{
  "detail": "Conversation with ID 999 not found"
}
```

### 409 Conflict
Constraint violation (e.g., duplicate tag).

```json
{
  "detail": "Tag already exists for this conversation"
}
```

### 500 Internal Server Error
Server error.

```json
{
  "detail": "Error creating conversation: ..."
}
```

---

## Testing with cURL

### Create a Conversation
```bash
curl -X POST "http://localhost:8000/api/chat/conversations" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_id": 1,
    "type": "support",
    "title": "Cannot submit report",
    "priority": "high",
    "created_by_user_id": 5,
    "participants": [
      {"user_id": 5, "role": "requester"}
    ],
    "tags": ["urgent"]
  }'
```

### Send a Message
```bash
curl -X POST "http://localhost:8000/api/chat/conversations/1/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_user_id": 5,
    "body": "I need help with the submission form.",
    "visibility": "public"
  }'
```

### Mark as Read
```bash
curl -X POST "http://localhost:8000/api/chat/messages/10/read" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3
  }'
```

### Add Reaction
```bash
curl -X POST "http://localhost:8000/api/chat/messages/10/reactions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "emoji": "👍"
  }'
```

---

## OpenAPI Documentation

Full interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide:
- Complete endpoint reference
- Request/response schemas
- Try-it-out functionality
- Example requests and responses

---

## Implementation Notes

### Database Constraints

All enum values are enforced at the database level via CHECK constraints:
- Invalid values will return `400 Bad Request`
- Foreign key violations will return `404 Not Found` or `400 Bad Request`
- Unique constraint violations will return `409 Conflict`

### Idempotency

The following operations are idempotent:
- Adding read receipts
- Adding reactions
- Adding participants (returns existing if duplicate)

### Visibility Control

Messages have two visibility levels:
- `public` - Visible to all participants
- `internal` - Visible only to staff (agent, observer, manager, administrator)

Always filter by `is_staff` parameter when listing messages.

### Timestamps

All timestamps are in UTC with timezone awareness (`timestamptz`).

### Pagination

- Conversations: Offset-based pagination (page/page_size)
- Messages: Cursor-based pagination (before_id/after_id)

---

## Next Steps

1. Implement authentication middleware to extract user from session
2. Add authorization checks using existing permission system
3. Implement file upload for attachments
4. Add WebSocket support for real-time messaging
5. Add full-text search across message bodies
6. Implement notification system (email/push)

---

## Related Documentation

- [Chat System Overview](CHAT_SYSTEM.md)
- [Chat System Summary](CHAT_SYSTEM_SUMMARY.md)
- [Database Migration](migrations/009_chat_schema.sql)

