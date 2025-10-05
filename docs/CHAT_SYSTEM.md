# Chat/Messaging System Documentation

## Overview

The chat system provides a comprehensive support conversation/ticketing platform for communication between clients (banking entities) and UKNF staff. It supports multi-party conversations, threaded messages, file attachments, read receipts, reactions, and assignment management.

## Architecture

### Database Schema

```
SUBJECTS (existing) ──┐
                      │
                      ├─> CONVERSATIONS ──┬─> CONVERSATION_PARTICIPANTS
                      │                   ├─> MESSAGES ──┬─> MESSAGE_ATTACHMENTS
USERS (existing) ─────┤                   │              ├─> READ_RECEIPTS
                      │                   │              └─> MESSAGE_REACTIONS
                      │                   ├─> CONVERSATION_TAGS
                      └───────────────────┴─> ASSIGNMENT_HISTORY
```

---

## Tables Reference

### 1. CONVERSATIONS

**Purpose:** Main conversation/ticket record within a single company (SUBJECT).

**Key Fields:**
- `SUBJECT_ID` - Reference to the banking entity
- `TYPE` - Conversation type (support/inquiry/complaint/consultation/report)
- `STATUS` - Current status (open/pending/resolved/closed/archived)
- `PRIORITY` - Priority level (low/normal/high/urgent/critical)
- `ASSIGNED_TO_USER_ID` - Currently assigned staff member
- `LAST_MESSAGE_AT` - Timestamp of last message (for sorting)

**Constraints:**
- Must belong to a SUBJECT (CASCADE delete)
- Created by must be a valid USER
- Assigned to must be a valid USER (optional)
- Type, status, and priority are strictly enforced via CHECK

**Indexes:**
- Subject ID (frequent queries by company)
- Status (filtering open/pending conversations)
- Assigned to (staff workload queries)
- Last message timestamp (sorting conversations)

---

### 2. CONVERSATION_PARTICIPANTS

**Purpose:** Track who is involved in each conversation and their role.

**Key Fields:**
- `CONVERSATION_ID` - Parent conversation
- `USER_ID` - Participant user
- `ROLE` - Participant role (requester/agent/observer/manager)
- `IS_ACTIVE` - Whether participant is still active

**Roles:**
- `requester` - The client/customer who initiated the conversation
- `agent` - Staff member handling the conversation
- `observer` - User monitoring the conversation (read-only)
- `manager` - Supervisor overseeing the conversation

**Constraints:**
- Unique combination of (CONVERSATION_ID, USER_ID, ROLE)
- Role strictly enforced via CHECK
- Cascade deletes with conversation and user

---

### 3. MESSAGES

**Purpose:** Store individual messages with threading support.

**Key Fields:**
- `CONVERSATION_ID` - Parent conversation
- `SENDER_USER_ID` - Message author
- `PARENT_MESSAGE_ID` - For threaded replies (optional)
- `BODY` - Message content (cannot be empty)
- `VISIBILITY` - public (visible to all) or internal (staff only)
- `MESSAGE_TYPE` - message/note/system/notification
- `IS_EDITED` - Flag if message was edited

**Message Types:**
- `message` - Regular conversation message
- `note` - Quick note or annotation
- `system` - System-generated message (e.g., "User X was assigned")
- `notification` - Automated notification

**Constraints:**
- Body cannot be empty (trimmed)
- Visibility strictly enforced (public/internal)
- Cascade deletes with conversation
- Parent message relationship (threading)

**Indexes:**
- Conversation ID + created timestamp (chronological display)
- Parent message ID (threading queries)
- Visibility filter (hide internal from clients)

---

### 4. MESSAGE_ATTACHMENTS

**Purpose:** Store file attachments linked to messages.

**Key Fields:**
- `MESSAGE_ID` - Parent message
- `FILE_NAME` - Original filename
- `FILE_PATH` - Storage path/URL
- `FILE_SIZE` - Size in bytes (max 100MB)
- `MIME_TYPE` - File type

**Constraints:**
- File size between 1 byte and 100MB
- Filename cannot be empty
- Cascade deletes with message

---

### 5. READ_RECEIPTS

**Purpose:** Track which users have read which messages.

**Key Fields:**
- `MESSAGE_ID` - Message that was read
- `USER_ID` - User who read it
- `READ_AT` - Timestamp

**Constraints:**
- Unique per (MESSAGE_ID, USER_ID)
- Cascade deletes with message and user

**Usage:**
- Insert when user opens/views a message
- Query to show "read by" indicators
- Calculate unread message counts

---

### 6. MESSAGE_REACTIONS

**Purpose:** Store emoji reactions to messages.

**Key Fields:**
- `MESSAGE_ID` - Message being reacted to
- `USER_ID` - User who reacted
- `EMOJI` - Emoji character(s)

**Constraints:**
- Unique per (MESSAGE_ID, USER_ID, EMOJI)
- Emoji cannot be empty
- Cascade deletes with message and user

**Usage:**
- Add: INSERT with ON CONFLICT DO NOTHING
- Remove: DELETE
- Display: GROUP BY emoji, COUNT users

---

### 7. CONVERSATION_TAGS

**Purpose:** Tag conversations for filtering and organization.

**Key Fields:**
- `CONVERSATION_ID` - Parent conversation
- `TAG` - Tag name (lowercase, alphanumeric, hyphens, underscores)
- `ADDED_BY_USER_ID` - Who added the tag

**Common Tags:**
- `vip` - VIP customer
- `urgent` - Urgent attention needed
- `sla-breach-risk` - At risk of SLA breach
- `technical-issue` - Technical problem
- `billing` - Billing related
- `escalated` - Escalated to management

**Constraints:**
- Tag format: `[a-z0-9\-_]+` (enforced via CHECK)
- Unique per (CONVERSATION_ID, TAG)
- Cascade deletes with conversation

**Indexes:**
- Tag name (filtering by tag)
- GIN trigram index (fuzzy search)

---

### 8. ASSIGNMENT_HISTORY

**Purpose:** Track history of conversation assignments.

**Key Fields:**
- `CONVERSATION_ID` - Conversation being assigned
- `ASSIGNED_FROM_USER_ID` - Previous assignee (nullable)
- `ASSIGNED_TO_USER_ID` - New assignee (nullable)
- `ASSIGNED_BY_USER_ID` - Who made the assignment
- `NOTE` - Assignment note/reason

**Constraints:**
- Cascade deletes with conversation
- Set NULL on user deletion (preserve history)

**Usage:**
- Record every assignment change
- Track workload distribution
- Audit trail for escalations

---

## Usage Patterns

### Creating a Conversation

```sql
-- Step 1: Create conversation
INSERT INTO "CONVERSATIONS" (
    "SUBJECT_ID", 
    "TYPE", 
    "CREATED_BY_USER_ID", 
    "TITLE", 
    "PRIORITY"
)
VALUES (
    1,              -- Banking entity ID
    'support',      -- Type
    5,              -- Client user ID
    'Cannot submit monthly report',
    'high'
)
RETURNING "ID";

-- Step 2: Add requester (client)
INSERT INTO "CONVERSATION_PARTICIPANTS" 
    ("CONVERSATION_ID", "USER_ID", "ROLE")
VALUES (1, 5, 'requester');

-- Step 3: Add agent (optional at creation)
INSERT INTO "CONVERSATION_PARTICIPANTS" 
    ("CONVERSATION_ID", "USER_ID", "ROLE")
VALUES (1, 3, 'agent');
```

---

### Sending Messages

**Public Message (visible to all):**

```sql
-- Insert message
INSERT INTO "MESSAGES" (
    "CONVERSATION_ID", 
    "SENDER_USER_ID", 
    "BODY", 
    "VISIBILITY"
)
VALUES (
    1, 
    5, 
    'I cannot access the report submission form.',
    'public'
);

-- Update conversation timestamp
UPDATE "CONVERSATIONS" 
SET "LAST_MESSAGE_AT" = NOW() 
WHERE "ID" = 1;
```

**Internal Note (staff only):**

```sql
INSERT INTO "MESSAGES" (
    "CONVERSATION_ID", 
    "SENDER_USER_ID", 
    "BODY", 
    "VISIBILITY",
    "MESSAGE_TYPE"
)
VALUES (
    1, 
    3, 
    'User needs password reset - checking with IT',
    'internal',
    'note'
);

UPDATE "CONVERSATIONS" 
SET "LAST_MESSAGE_AT" = NOW() 
WHERE "ID" = 1;
```

**Threaded Reply:**

```sql
-- Reply to message ID 10
INSERT INTO "MESSAGES" (
    "CONVERSATION_ID", 
    "SENDER_USER_ID", 
    "PARENT_MESSAGE_ID",
    "BODY", 
    "VISIBILITY"
)
VALUES (
    1, 
    3,
    10,  -- Parent message ID
    'I have reset your password. Please check your email.',
    'public'
);
```

---

### Assignment Management

**Assign to Staff Member:**

```sql
-- Update conversation
UPDATE "CONVERSATIONS" 
SET "ASSIGNED_TO_USER_ID" = 3 
WHERE "ID" = 1;

-- Record in history
INSERT INTO "ASSIGNMENT_HISTORY" (
    "CONVERSATION_ID", 
    "ASSIGNED_TO_USER_ID", 
    "ASSIGNED_BY_USER_ID", 
    "NOTE"
)
VALUES (
    1, 
    3,  -- Assigned to user 3
    2,  -- Assigned by user 2 (manager)
    'Assigned to senior agent for technical issue'
);
```

**Reassign:**

```sql
-- Update conversation
UPDATE "CONVERSATIONS" 
SET "ASSIGNED_TO_USER_ID" = 7 
WHERE "ID" = 1;

-- Record reassignment
INSERT INTO "ASSIGNMENT_HISTORY" (
    "CONVERSATION_ID", 
    "ASSIGNED_FROM_USER_ID",
    "ASSIGNED_TO_USER_ID", 
    "ASSIGNED_BY_USER_ID", 
    "NOTE"
)
VALUES (
    1,
    3,  -- Previous assignee
    7,  -- New assignee
    2,  -- Assigned by
    'Escalated to team lead'
);
```

---

### Read Receipts

```sql
-- Mark message as read
INSERT INTO "READ_RECEIPTS" ("MESSAGE_ID", "USER_ID")
VALUES (10, 3)
ON CONFLICT ("MESSAGE_ID", "USER_ID") DO NOTHING;

-- Query unread messages for user
SELECT m.*
FROM "MESSAGES" m
LEFT JOIN "READ_RECEIPTS" rr 
    ON m."ID" = rr."MESSAGE_ID" 
    AND rr."USER_ID" = 3
WHERE m."CONVERSATION_ID" = 1
  AND rr."ID" IS NULL
  AND m."DELETED_AT" IS NULL
ORDER BY m."CREATED_AT" ASC;
```

---

### Reactions

```sql
-- Add reaction
INSERT INTO "MESSAGE_REACTIONS" ("MESSAGE_ID", "USER_ID", "EMOJI")
VALUES (10, 3, '👍')
ON CONFLICT ("MESSAGE_ID", "USER_ID", "EMOJI") DO NOTHING;

-- Remove reaction
DELETE FROM "MESSAGE_REACTIONS"
WHERE "MESSAGE_ID" = 10 
  AND "USER_ID" = 3 
  AND "EMOJI" = '👍';

-- Get reaction summary
SELECT 
    "EMOJI",
    COUNT(*) as count,
    ARRAY_AGG("USER_ID") as user_ids
FROM "MESSAGE_REACTIONS"
WHERE "MESSAGE_ID" = 10
GROUP BY "EMOJI";
```

---

### Tags

```sql
-- Add tags
INSERT INTO "CONVERSATION_TAGS" 
    ("CONVERSATION_ID", "TAG", "ADDED_BY_USER_ID")
VALUES 
    (1, 'vip', 2),
    (1, 'urgent', 2),
    (1, 'technical-issue', 2);

-- Filter conversations by tag
SELECT c.*
FROM "CONVERSATIONS" c
INNER JOIN "CONVERSATION_TAGS" ct 
    ON c."ID" = ct."CONVERSATION_ID"
WHERE ct."TAG" = 'urgent'
  AND c."STATUS" IN ('open', 'pending')
ORDER BY c."LAST_MESSAGE_AT" DESC;

-- Multiple tags (AND logic)
SELECT c.*
FROM "CONVERSATIONS" c
WHERE c."ID" IN (
    SELECT "CONVERSATION_ID"
    FROM "CONVERSATION_TAGS"
    WHERE "TAG" IN ('vip', 'urgent')
    GROUP BY "CONVERSATION_ID"
    HAVING COUNT(DISTINCT "TAG") = 2
);
```

---

## Common Queries

### Staff Dashboard - Assigned Conversations

```sql
SELECT 
    c.*,
    s."NAME_STRUCTURE" as subject_name,
    COUNT(DISTINCT m."ID") FILTER (WHERE m."VISIBILITY" = 'public') as message_count,
    COUNT(DISTINCT rr."ID") as read_count
FROM "CONVERSATIONS" c
INNER JOIN "SUBJECTS" s ON c."SUBJECT_ID" = s."ID"
LEFT JOIN "MESSAGES" m ON c."ID" = m."CONVERSATION_ID"
LEFT JOIN "READ_RECEIPTS" rr ON m."ID" = rr."MESSAGE_ID"
WHERE c."ASSIGNED_TO_USER_ID" = 3  -- Current user
  AND c."STATUS" IN ('open', 'pending')
GROUP BY c."ID", s."NAME_STRUCTURE"
ORDER BY c."PRIORITY" DESC, c."LAST_MESSAGE_AT" DESC;
```

### Conversation Detail with Latest Messages

```sql
SELECT 
    m.*,
    u."USER_NAME",
    u."USER_LASTNAME",
    COUNT(DISTINCT ma."ID") as attachment_count,
    COUNT(DISTINCT rr."ID") as read_count,
    ARRAY_AGG(DISTINCT mr."EMOJI") FILTER (WHERE mr."EMOJI" IS NOT NULL) as reactions
FROM "MESSAGES" m
INNER JOIN "USERS" u ON m."SENDER_USER_ID" = u."ID"
LEFT JOIN "MESSAGE_ATTACHMENTS" ma ON m."ID" = ma."MESSAGE_ID"
LEFT JOIN "READ_RECEIPTS" rr ON m."ID" = rr."MESSAGE_ID"
LEFT JOIN "MESSAGE_REACTIONS" mr ON m."ID" = mr."MESSAGE_ID"
WHERE m."CONVERSATION_ID" = 1
  AND m."DELETED_AT" IS NULL
  AND (m."VISIBILITY" = 'public' OR :is_staff = true)
GROUP BY m."ID", u."USER_NAME", u."USER_LASTNAME"
ORDER BY m."CREATED_AT" ASC;
```

---

## Performance Considerations

### Indexes

All frequently queried columns have indexes:
- Conversation lookups by subject, status, assignee
- Message lookups by conversation, sender
- Read receipt queries by message and user
- Tag-based filtering with GIN trigram index

### Cascading Deletes

Deleting a conversation automatically removes:
- All participants
- All messages (and their attachments, receipts, reactions)
- All tags
- Assignment history

### JSON Metadata

Both `CONVERSATIONS` and `MESSAGES` have `METADATA` JSONB fields for extensibility without schema changes.

---

## Security Considerations

### Visibility Control

**Public Messages:**
- Visible to all participants
- Include in notifications
- Display in client interface

**Internal Messages:**
- Visible only to staff (agents, observers, managers)
- Never show to requesters
- Use for notes, discussions, escalation

**Query Pattern:**
```sql
WHERE m."VISIBILITY" = 'public' 
   OR (m."VISIBILITY" = 'internal' AND :user_role IN ('agent', 'observer', 'manager'))
```

### Role-Based Access

Check participant role before allowing actions:
- **Requester**: Can send public messages, view public messages
- **Agent**: Can send public/internal messages, assign conversations
- **Observer**: Read-only access to everything
- **Manager**: Full access, can reassign, escalate

---

## Migration Application

To apply this migration:

```bash
# If using Docker Compose (automatic on container start)
docker-compose down
docker-compose up -d

# Or manually with psql
psql -U myuser -d mydatabase -f migrations/009_chat_schema.sql
```

Verify migration:

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE '%CONVERSATION%' 
   OR table_name LIKE '%MESSAGE%';

-- Check indexes
SELECT indexname 
FROM pg_indexes 
WHERE tablename IN (
    'CONVERSATIONS', 
    'MESSAGES', 
    'CONVERSATION_PARTICIPANTS'
);
```

---

## Next Steps

1. **API Implementation**: Create FastAPI endpoints for chat functionality
2. **WebSocket Support**: Add real-time message delivery
3. **Notifications**: Email/push notifications for new messages
4. **File Storage**: Implement secure file upload/download for attachments
5. **Search**: Full-text search across message bodies
6. **Analytics**: Conversation metrics, response times, SLA tracking

---

## Related Documentation

- [Main Project Analysis](README.md)
- [PESEL Masking](PESEL_MASKING.md)
- [Database Migrations](migrations/)

