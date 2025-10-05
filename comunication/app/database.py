"""
Database table definitions for chat system
"""
from sqlalchemy import MetaData, Table, Column, BigInteger, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB


metadata = MetaData()

# Chat tables (matching migration 009_chat_schema.sql)

conversations = Table(
    "CONVERSATIONS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("SUBJECT_ID", BigInteger),
    Column("TYPE", String(50)),
    Column("STATUS", String(50)),
    Column("PRIORITY", String(50)),
    Column("TITLE", String(500)),
    Column("CREATED_BY_USER_ID", BigInteger),
    Column("ASSIGNED_TO_USER_ID", BigInteger),
    Column("CREATED_AT", DateTime(timezone=True)),
    Column("UPDATED_AT", DateTime(timezone=True)),
    Column("CLOSED_AT", DateTime(timezone=True)),
    Column("LAST_MESSAGE_AT", DateTime(timezone=True)),
    Column("METADATA", JSONB),
)

conversation_participants = Table(
    "CONVERSATION_PARTICIPANTS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("CONVERSATION_ID", BigInteger),
    Column("USER_ID", BigInteger),
    Column("ROLE", String(50)),
    Column("JOINED_AT", DateTime(timezone=True)),
    Column("LEFT_AT", DateTime(timezone=True)),
    Column("IS_ACTIVE", Boolean),
)

messages = Table(
    "MESSAGES",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("CONVERSATION_ID", BigInteger),
    Column("SENDER_USER_ID", BigInteger),
    Column("PARENT_MESSAGE_ID", BigInteger),
    Column("BODY", Text),
    Column("VISIBILITY", String(50)),
    Column("MESSAGE_TYPE", String(50)),
    Column("CREATED_AT", DateTime(timezone=True)),
    Column("UPDATED_AT", DateTime(timezone=True)),
    Column("DELETED_AT", DateTime(timezone=True)),
    Column("IS_EDITED", Boolean),
    Column("METADATA", JSONB),
)

message_attachments = Table(
    "MESSAGE_ATTACHMENTS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("MESSAGE_ID", BigInteger),
    Column("FILE_NAME", String(500)),
    Column("FILE_PATH", String(1000)),
    Column("FILE_SIZE", BigInteger),
    Column("MIME_TYPE", String(255)),
    Column("UPLOADED_BY_USER_ID", BigInteger),
    Column("UPLOADED_AT", DateTime(timezone=True)),
    Column("METADATA", JSONB),
)

read_receipts = Table(
    "READ_RECEIPTS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("MESSAGE_ID", BigInteger),
    Column("USER_ID", BigInteger),
    Column("READ_AT", DateTime(timezone=True)),
)

message_reactions = Table(
    "MESSAGE_REACTIONS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("MESSAGE_ID", BigInteger),
    Column("USER_ID", BigInteger),
    Column("EMOJI", String(50)),
    Column("CREATED_AT", DateTime(timezone=True)),
)

conversation_tags = Table(
    "CONVERSATION_TAGS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("CONVERSATION_ID", BigInteger),
    Column("TAG", String(100)),
    Column("ADDED_BY_USER_ID", BigInteger),
    Column("ADDED_AT", DateTime(timezone=True)),
)

assignment_history = Table(
    "ASSIGNMENT_HISTORY",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("CONVERSATION_ID", BigInteger),
    Column("ASSIGNED_FROM_USER_ID", BigInteger),
    Column("ASSIGNED_TO_USER_ID", BigInteger),
    Column("ASSIGNED_BY_USER_ID", BigInteger),
    Column("ASSIGNED_AT", DateTime(timezone=True)),
    Column("NOTE", Text),
)

# Existing tables (for reference checks)
subjects = Table(
    "SUBJECTS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
)

users = Table(
    "USERS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
)

users_groups = Table(
    "USERS_GROUPS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("USER_ID", BigInteger),
    Column("GROUP_ID", BigInteger),
)

groups = Table(
    "GROUPS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("GROUP_NAME", String(250)),
)

