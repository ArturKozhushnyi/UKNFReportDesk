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

# Reporting tables (from migration 011)
report_status_dict = Table(
    "REPORT_STATUS_DICT",
    metadata,
    Column("CODE", String(50), primary_key=True),
    Column("LABEL", String(200)),
    Column("ORDER_NUM", BigInteger),
    Column("FINAL", Boolean),
)

report_types = Table(
    "REPORT_TYPES",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("CODE", String(100)),
    Column("NAME", String(300)),
    Column("CATEGORY", String(30)),
)

report_templates = Table(
    "REPORT_TEMPLATES",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("REPORT_TYPE_ID", BigInteger),
    Column("VERSION", String(50)),
    Column("STORAGE_URL", String(2000)),
    Column("ACTIVE_FROM", DateTime),
    Column("ACTIVE_TO", DateTime),
)

reporting_periods = Table(
    "REPORTING_PERIODS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("PERIOD_TYPE", String(20)),
    Column("YEAR", BigInteger),
    Column("QUARTER", BigInteger),
    Column("START_DATE", DateTime),
    Column("END_DATE", DateTime),
)

expected_reports = Table(
    "EXPECTED_REPORTS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("SUBJECT_ID", BigInteger),
    Column("REPORT_TYPE_ID", BigInteger),
    Column("PERIOD_ID", BigInteger),
    Column("DUE_AT", DateTime(timezone=True)),
    Column("STATUS", String(20)),
    Column("DATE_CREATE", DateTime(timezone=True)),
)

reports = Table(
    "REPORTS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("SUBJECT_ID", BigInteger),
    Column("REPORT_TYPE_ID", BigInteger),
    Column("PERIOD_ID", BigInteger),
    Column("CREATED_BY_USER_ID", BigInteger),
    Column("CURRENT_STATUS", String(50)),
    Column("HAS_CORRECTION", Boolean),
    Column("IS_ARCHIVED", Boolean),
    Column("ARCHIVED_AT", DateTime(timezone=True)),
    Column("DATE_CREATE", DateTime(timezone=True)),
    Column("DATE_ACTUALIZATION", DateTime(timezone=True)),
)

report_files = Table(
    "REPORT_FILES",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("REPORT_ID", BigInteger),
    Column("VERSION_NO", BigInteger),
    Column("UPLOADED_BY_USER_ID", BigInteger),
    Column("ORIGINAL_FILE_NAME", String(500)),
    Column("MIME_TYPE", String(150)),
    Column("SIZE_BYTES", BigInteger),
    Column("STORAGE_URL", String(2000)),
    Column("UPLOADED_AT", DateTime(timezone=True)),
)

validation_runs = Table(
    "VALIDATION_RUNS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("REPORT_FILE_ID", BigInteger),
    Column("EXTERNAL_JOB_ID", String(200)),
    Column("STATUS", String(50)),
    Column("METADATA", JSONB),
    Column("REPORT_LINK_URL", String(2000)),
    Column("STARTED_AT", DateTime(timezone=True)),
    Column("FINISHED_AT", DateTime(timezone=True)),
)

validation_errors = Table(
    "VALIDATION_ERRORS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("VALIDATION_RUN_ID", BigInteger),
    Column("RULE_CODE", String(200)),
    Column("SEVERITY", String(20)),
    Column("MESSAGE", Text),
    Column("SHEET", String(200)),
    Column("ROW_NUM", BigInteger),
    Column("COLUMN_NAME", String(200)),
    Column("CELL_REF", String(50)),
    Column("CONTEXT", JSONB),
)

report_status_history = Table(
    "REPORT_STATUS_HISTORY",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("REPORT_ID", BigInteger),
    Column("STATUS_CODE", String(50)),
    Column("CHANGED_AT", DateTime(timezone=True)),
    Column("CHANGED_BY_USER_ID", BigInteger),
    Column("NOTE", String(1000)),
)

report_conversations = Table(
    "REPORT_CONVERSATIONS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("REPORT_ID", BigInteger),
    Column("CONVERSATION_ID", BigInteger),
)

report_reminders = Table(
    "REPORT_REMINDERS",
    metadata,
    Column("ID", BigInteger, primary_key=True),
    Column("SUBJECT_ID", BigInteger),
    Column("REPORT_TYPE_ID", BigInteger),
    Column("PERIOD_ID", BigInteger),
    Column("REMIND_AT", DateTime(timezone=True)),
    Column("CREATED_BY_USER_ID", BigInteger),
    Column("STATUS", String(20)),
    Column("PAYLOAD", JSONB),
)

