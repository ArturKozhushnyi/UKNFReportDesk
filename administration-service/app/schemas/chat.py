"""
Pydantic schemas for chat/messaging system
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Enums (matching database CHECK constraints)
# ============================================================================

ConversationType = Literal['support', 'inquiry', 'complaint', 'consultation', 'report']
ConversationStatus = Literal['open', 'pending', 'resolved', 'closed', 'archived']
ConversationPriority = Literal['low', 'normal', 'high', 'urgent', 'critical']
ParticipantRole = Literal['requester', 'agent', 'observer', 'manager']
MessageVisibility = Literal['public', 'internal']
MessageType = Literal['message', 'note', 'system', 'notification']


# ============================================================================
# Conversation Schemas
# ============================================================================

class ParticipantCreate(BaseModel):
    user_id: int
    role: ParticipantRole


class ConversationCreate(BaseModel):
    subject_id: int
    type: ConversationType
    title: Optional[str] = None
    priority: ConversationPriority = 'normal'
    created_by_user_id: int
    assigned_to_user_id: Optional[int] = None
    participants: Optional[List[ParticipantCreate]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
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
    })


class ConversationUpdate(BaseModel):
    status: Optional[ConversationStatus] = None
    priority: Optional[ConversationPriority] = None
    assigned_to_user_id: Optional[int] = None
    title: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status": "resolved",
            "priority": "normal",
            "assigned_to_user_id": 7
        }
    })


class ParticipantOut(BaseModel):
    ID: int
    CONVERSATION_ID: int
    USER_ID: int
    ROLE: ParticipantRole
    JOINED_AT: datetime
    LEFT_AT: Optional[datetime] = None
    IS_ACTIVE: bool

    model_config = ConfigDict(from_attributes=True)


class ConversationOut(BaseModel):
    ID: int
    SUBJECT_ID: int
    TYPE: ConversationType
    STATUS: ConversationStatus
    PRIORITY: ConversationPriority
    TITLE: Optional[str] = None
    CREATED_BY_USER_ID: int
    ASSIGNED_TO_USER_ID: Optional[int] = None
    CREATED_AT: datetime
    UPDATED_AT: datetime
    CLOSED_AT: Optional[datetime] = None
    LAST_MESSAGE_AT: Optional[datetime] = None
    METADATA: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationDetail(ConversationOut):
    participants: List[ParticipantOut] = []
    tags: List[str] = []


class ConversationListResponse(BaseModel):
    items: List[ConversationOut]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Message Schemas
# ============================================================================

class MessageCreate(BaseModel):
    sender_user_id: int
    body: str = Field(..., min_length=1, max_length=50000)
    visibility: MessageVisibility = 'public'
    message_type: MessageType = 'message'
    parent_message_id: Optional[int] = None
    metadata: Optional[dict] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "sender_user_id": 5,
            "body": "I cannot access the report submission form.",
            "visibility": "public",
            "message_type": "message"
        }
    })


class MessageUpdate(BaseModel):
    body: Optional[str] = Field(None, min_length=1, max_length=50000)
    visibility: Optional[MessageVisibility] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "body": "I cannot access the report submission form. Error code: ERR_403",
            "visibility": "public"
        }
    })


class MessageOut(BaseModel):
    ID: int
    CONVERSATION_ID: int
    SENDER_USER_ID: int
    PARENT_MESSAGE_ID: Optional[int] = None
    BODY: str
    VISIBILITY: MessageVisibility
    MESSAGE_TYPE: MessageType
    CREATED_AT: datetime
    UPDATED_AT: Optional[datetime] = None
    DELETED_AT: Optional[datetime] = None
    IS_EDITED: bool
    METADATA: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    items: List[MessageOut]
    total: int
    has_more: bool


# ============================================================================
# Participant Schemas
# ============================================================================

class ParticipantAdd(BaseModel):
    user_id: int
    role: ParticipantRole = 'observer'

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": 7,
            "role": "observer"
        }
    })


# ============================================================================
# Tag Schemas
# ============================================================================

class TagCreate(BaseModel):
    tag: str = Field(..., pattern=r'^[a-z0-9\-_]+$', min_length=1, max_length=100)
    added_by_user_id: int

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "tag": "vip",
            "added_by_user_id": 3
        }
    })


class TagOut(BaseModel):
    ID: int
    CONVERSATION_ID: int
    TAG: str
    ADDED_BY_USER_ID: int
    ADDED_AT: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Attachment Schemas
# ============================================================================

class AttachmentCreate(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=500)
    file_path: str = Field(..., min_length=1, max_length=1000)
    file_size: int = Field(..., gt=0, le=104857600)  # Max 100MB
    mime_type: str = Field(..., min_length=1, max_length=255)
    uploaded_by_user_id: int
    metadata: Optional[dict] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "file_name": "report_error_screenshot.png",
            "file_path": "/uploads/2025/10/abc123.png",
            "file_size": 245678,
            "mime_type": "image/png",
            "uploaded_by_user_id": 5
        }
    })


class AttachmentOut(BaseModel):
    ID: int
    MESSAGE_ID: int
    FILE_NAME: str
    FILE_PATH: str
    FILE_SIZE: int
    MIME_TYPE: str
    UPLOADED_BY_USER_ID: int
    UPLOADED_AT: datetime
    METADATA: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Read Receipt Schemas
# ============================================================================

class ReadReceiptCreate(BaseModel):
    user_id: int
    read_at: Optional[datetime] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": 3
        }
    })


class ReadReceiptOut(BaseModel):
    ID: int
    MESSAGE_ID: int
    USER_ID: int
    READ_AT: datetime

    model_config = ConfigDict(from_attributes=True)


class UnreadCount(BaseModel):
    conversation_id: int
    unread_count: int


class UnreadSummary(BaseModel):
    items: List[UnreadCount]
    total_unread: int


# ============================================================================
# Reaction Schemas
# ============================================================================

class ReactionCreate(BaseModel):
    user_id: int
    emoji: str = Field(..., min_length=1, max_length=50)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": 3,
            "emoji": "👍"
        }
    })


class ReactionDelete(BaseModel):
    user_id: int
    emoji: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": 3,
            "emoji": "👍"
        }
    })


class ReactionOut(BaseModel):
    ID: int
    MESSAGE_ID: int
    USER_ID: int
    EMOJI: str
    CREATED_AT: datetime

    model_config = ConfigDict(from_attributes=True)


class ReactionSummary(BaseModel):
    emoji: str
    count: int
    user_ids: List[int]


# ============================================================================
# Assignment Schemas
# ============================================================================

class AssignmentCreate(BaseModel):
    assigned_to_user_id: Optional[int] = None
    note: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "assigned_to_user_id": 7,
            "note": "Escalated to senior agent for complex technical issue"
        }
    })


class AssignmentOut(BaseModel):
    ID: int
    CONVERSATION_ID: int
    ASSIGNED_FROM_USER_ID: Optional[int] = None
    ASSIGNED_TO_USER_ID: Optional[int] = None
    ASSIGNED_BY_USER_ID: int
    ASSIGNED_AT: datetime
    NOTE: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

