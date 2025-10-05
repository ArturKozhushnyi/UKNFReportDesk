"""
Chat/Messaging System Router
Implements conversation, message, participant, tag, attachment, read receipt, reaction, and assignment endpoints
"""
import math
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, insert, update, delete, func, and_, or_, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import httpx

from app.schemas.chat import (
    ConversationCreate, ConversationUpdate, ConversationOut, ConversationDetail, ConversationListResponse,
    MessageCreate, MessageUpdate, MessageOut, MessageListResponse,
    ParticipantAdd, ParticipantOut,
    TagCreate, TagOut,
    AttachmentCreate, AttachmentOut,
    ReadReceiptCreate, ReadReceiptOut, UnreadCount, UnreadSummary,
    ReactionCreate, ReactionDelete, ReactionOut, ReactionSummary,
    AssignmentCreate, AssignmentOut,
)
from app.database import (
    conversations, conversation_participants, messages, message_attachments,
    read_receipts, message_reactions, conversation_tags, assignment_history,
    subjects, users, groups, users_groups
)


router = APIRouter(prefix="/chat", tags=["Chat"])


# ============================================================================
# Dependencies
# ============================================================================

def get_db():
    """Database session dependency - reuse from main app"""
    from main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(authorization: str = Depends(lambda: None)) -> Optional[int]:
    """
    Extract user ID from session (simplified for demo)
    In production, this should validate the session via auth-service
    """
    # For now, this is a placeholder - you should implement actual session validation
    # by calling your auth-service /authz endpoint
    return None  # Will be replaced with actual user ID from session


def check_conversation_access(conversation_id: int, user_id: int, db: Session) -> bool:
    """
    Check if user has access to a conversation
    User has access if they are a participant OR have staff/admin privileges
    """
    # Check if user is a participant
    stmt = select(conversation_participants).where(
        and_(
            conversation_participants.c.CONVERSATION_ID == conversation_id,
            conversation_participants.c.USER_ID == user_id,
            conversation_participants.c.IS_ACTIVE == True
        )
    )
    result = db.execute(stmt)
    if result.fetchone():
        return True
    
    # Check if user is in administrator group
    stmt = select(users_groups).join(
        groups, users_groups.c.GROUP_ID == groups.c.ID
    ).where(
        and_(
            users_groups.c.USER_ID == user_id,
            groups.c.GROUP_NAME == 'administrator'
        )
    )
    result = db.execute(stmt)
    if result.fetchone():
        return True
    
    return False


def is_staff_user(user_id: int, db: Session) -> bool:
    """Check if user is staff (agent, observer, manager) or administrator"""
    stmt = select(conversation_participants).where(
        and_(
            conversation_participants.c.USER_ID == user_id,
            conversation_participants.c.ROLE.in_(['agent', 'observer', 'manager'])
        )
    ).limit(1)
    result = db.execute(stmt)
    if result.fetchone():
        return True
    
    # Check administrator group
    stmt = select(users_groups).join(
        groups, users_groups.c.GROUP_ID == groups.c.ID
    ).where(
        and_(
            users_groups.c.USER_ID == user_id,
            groups.c.GROUP_NAME == 'administrator'
        )
    )
    result = db.execute(stmt)
    return result.fetchone() is not None


# ============================================================================
# Conversation Endpoints
# ============================================================================

@router.post(
    "/conversations",
    response_model=ConversationDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
    description="Create a conversation with participants and optional tags"
)
def create_conversation(
    conv_data: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation/ticket.
    
    - Validates that SUBJECT_ID exists
    - Creates conversation record
    - Adds participants (at least requester)
    - Adds tags if provided
    - Returns complete conversation with participants and tags
    """
    try:
        # Validate subject exists
        stmt = select(subjects).where(subjects.c.ID == conv_data.subject_id)
        result = db.execute(stmt)
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject with ID {conv_data.subject_id} not found"
            )
        
        # Validate created_by user exists
        stmt = select(users).where(users.c.ID == conv_data.created_by_user_id)
        result = db.execute(stmt)
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {conv_data.created_by_user_id} not found"
            )
        
        # Validate assigned_to user if provided
        if conv_data.assigned_to_user_id:
            stmt = select(users).where(users.c.ID == conv_data.assigned_to_user_id)
            result = db.execute(stmt)
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {conv_data.assigned_to_user_id} not found"
                )
        
        # Create conversation
        now = datetime.now(timezone.utc)
        stmt = insert(conversations).values(
            SUBJECT_ID=conv_data.subject_id,
            TYPE=conv_data.type,
            STATUS='open',
            PRIORITY=conv_data.priority,
            TITLE=conv_data.title,
            CREATED_BY_USER_ID=conv_data.created_by_user_id,
            ASSIGNED_TO_USER_ID=conv_data.assigned_to_user_id,
            CREATED_AT=now,
            UPDATED_AT=now,
            METADATA=conv_data.metadata
        ).returning(conversations)
        result = db.execute(stmt)
        conv_row = result.fetchone()
        conversation_id = conv_row.ID
        
        # Add participants
        participants_list = conv_data.participants or []
        if not any(p.user_id == conv_data.created_by_user_id for p in participants_list):
            # Ensure creator is a participant
            participants_list.append(
                type('obj', (object,), {'user_id': conv_data.created_by_user_id, 'role': 'requester'})()
            )
        
        participant_records = []
        for p in participants_list:
            stmt = insert(conversation_participants).values(
                CONVERSATION_ID=conversation_id,
                USER_ID=p.user_id,
                ROLE=p.role,
                JOINED_AT=now,
                IS_ACTIVE=True
            ).returning(conversation_participants)
            result = db.execute(stmt)
            participant_records.append(result.fetchone())
        
        # Add tags if provided
        tag_list = []
        if conv_data.tags:
            for tag in conv_data.tags:
                try:
                    stmt = insert(conversation_tags).values(
                        CONVERSATION_ID=conversation_id,
                        TAG=tag.lower(),
                        ADDED_BY_USER_ID=conv_data.created_by_user_id,
                        ADDED_AT=now
                    )
                    db.execute(stmt)
                    tag_list.append(tag.lower())
                except IntegrityError:
                    # Tag already exists, skip
                    db.rollback()
                    pass
        
        # Create assignment history if assigned
        if conv_data.assigned_to_user_id:
            stmt = insert(assignment_history).values(
                CONVERSATION_ID=conversation_id,
                ASSIGNED_TO_USER_ID=conv_data.assigned_to_user_id,
                ASSIGNED_BY_USER_ID=conv_data.created_by_user_id,
                ASSIGNED_AT=now,
                NOTE="Initial assignment"
            )
            db.execute(stmt)
        
        db.commit()
        
        # Return complete conversation
        return ConversationDetail(
            **dict(conv_row._mapping),
            participants=[ParticipantOut(**dict(p._mapping)) for p in participant_records],
            tags=tag_list
        )
        
    except IntegrityError as e:
        db.rollback()
        if "TYPE" in str(e) or "STATUS" in str(e) or "PRIORITY" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid enum value for type, status, or priority"
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Database constraint violation: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="List conversations",
    description="Get paginated list of conversations with filtering"
)
def list_conversations(
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to_user_id: Optional[int] = Query(None, description="Filter by assigned user"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    q: Optional[str] = Query(None, description="Search in title"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("last_message_at_desc", description="Sort field (last_message_at_desc, created_at_desc, priority)"),
    db: Session = Depends(get_db)
):
    """
    List conversations with filtering, pagination, and sorting.
    """
    # Build query
    query = select(conversations)
    
    # Apply filters
    conditions = []
    if subject_id:
        conditions.append(conversations.c.SUBJECT_ID == subject_id)
    if status:
        conditions.append(conversations.c.STATUS == status)
    if priority:
        conditions.append(conversations.c.PRIORITY == priority)
    if assigned_to_user_id:
        conditions.append(conversations.c.ASSIGNED_TO_USER_ID == assigned_to_user_id)
    if q:
        conditions.append(conversations.c.TITLE.ilike(f"%{q}%"))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Filter by tag if provided
    if tag:
        subquery = select(conversation_tags.c.CONVERSATION_ID).where(
            conversation_tags.c.TAG == tag.lower()
        )
        query = query.where(conversations.c.ID.in_(subquery))
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()
    
    # Apply sorting
    if sort == "last_message_at_desc":
        query = query.order_by(conversations.c.LAST_MESSAGE_AT.desc().nulls_last())
    elif sort == "created_at_desc":
        query = query.order_by(conversations.c.CREATED_AT.desc())
    elif sort == "priority":
        # Sort by priority enum order
        priority_order = text("CASE PRIORITY WHEN 'critical' THEN 1 WHEN 'urgent' THEN 2 WHEN 'high' THEN 3 WHEN 'normal' THEN 4 WHEN 'low' THEN 5 END")
        query = query.order_by(priority_order, conversations.c.CREATED_AT.desc())
    else:
        query = query.order_by(conversations.c.CREATED_AT.desc())
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = db.execute(query)
    items = [ConversationOut(**dict(row._mapping)) for row in result.fetchall()]
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return ConversationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetail,
    summary="Get conversation details",
    description="Get conversation with participants and tags"
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation by ID with participants and tags."""
    # Get conversation
    stmt = select(conversations).where(conversations.c.ID == conversation_id)
    result = db.execute(stmt)
    conv_row = result.fetchone()
    
    if not conv_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Get participants
    stmt = select(conversation_participants).where(
        conversation_participants.c.CONVERSATION_ID == conversation_id
    )
    result = db.execute(stmt)
    participants_list = [ParticipantOut(**dict(row._mapping)) for row in result.fetchall()]
    
    # Get tags
    stmt = select(conversation_tags.c.TAG).where(
        conversation_tags.c.CONVERSATION_ID == conversation_id
    )
    result = db.execute(stmt)
    tag_list = [row.TAG for row in result.fetchall()]
    
    return ConversationDetail(
        **dict(conv_row._mapping),
        participants=participants_list,
        tags=tag_list
    )


@router.patch(
    "/conversations/{conversation_id}",
    response_model=ConversationOut,
    summary="Update conversation",
    description="Update conversation fields (status, priority, assigned user)"
)
def update_conversation(
    conversation_id: int,
    conv_update: ConversationUpdate,
    current_user_id: int = Query(..., description="Current user ID"),
    db: Session = Depends(get_db)
):
    """
    Update conversation fields.
    If assigned_to_user_id changes, records assignment history.
    """
    # Get current conversation
    stmt = select(conversations).where(conversations.c.ID == conversation_id)
    result = db.execute(stmt)
    current_conv = result.fetchone()
    
    if not current_conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    try:
        # Build update dict
        update_dict = {}
        if conv_update.status is not None:
            update_dict["STATUS"] = conv_update.status
            if conv_update.status == "closed" and not current_conv.CLOSED_AT:
                update_dict["CLOSED_AT"] = datetime.now(timezone.utc)
        if conv_update.priority is not None:
            update_dict["PRIORITY"] = conv_update.priority
        if conv_update.title is not None:
            update_dict["TITLE"] = conv_update.title
        
        # Handle assignment change
        old_assigned_to = current_conv.ASSIGNED_TO_USER_ID
        new_assigned_to = conv_update.assigned_to_user_id if conv_update.assigned_to_user_id is not None else old_assigned_to
        
        if new_assigned_to != old_assigned_to:
            update_dict["ASSIGNED_TO_USER_ID"] = new_assigned_to
            
            # Record assignment history
            stmt = insert(assignment_history).values(
                CONVERSATION_ID=conversation_id,
                ASSIGNED_FROM_USER_ID=old_assigned_to,
                ASSIGNED_TO_USER_ID=new_assigned_to,
                ASSIGNED_BY_USER_ID=current_user_id,
                ASSIGNED_AT=datetime.now(timezone.utc),
                NOTE="Assignment changed via API"
            )
            db.execute(stmt)
        
        if update_dict:
            update_dict["UPDATED_AT"] = datetime.now(timezone.utc)
            stmt = update(conversations).where(
                conversations.c.ID == conversation_id
            ).values(**update_dict).returning(conversations)
            result = db.execute(stmt)
            updated_row = result.fetchone()
            db.commit()
            return ConversationOut(**dict(updated_row._mapping))
        else:
            return ConversationOut(**dict(current_conv._mapping))
            
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid value: {str(e)}"
        )


# ============================================================================
# Message Endpoints
# ============================================================================

@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message",
    description="Create a new message in a conversation"
)
def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Send a message in a conversation.
    Updates LAST_MESSAGE_AT on the conversation.
    """
    # Verify conversation exists
    stmt = select(conversations).where(conversations.c.ID == conversation_id)
    result = db.execute(stmt)
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Verify parent message if provided
    if message_data.parent_message_id:
        stmt = select(messages).where(messages.c.ID == message_data.parent_message_id)
        result = db.execute(stmt)
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent message with ID {message_data.parent_message_id} not found"
            )
    
    try:
        now = datetime.now(timezone.utc)
        
        # Insert message
        stmt = insert(messages).values(
            CONVERSATION_ID=conversation_id,
            SENDER_USER_ID=message_data.sender_user_id,
            PARENT_MESSAGE_ID=message_data.parent_message_id,
            BODY=message_data.body,
            VISIBILITY=message_data.visibility,
            MESSAGE_TYPE=message_data.message_type,
            CREATED_AT=now,
            IS_EDITED=False,
            METADATA=message_data.metadata
        ).returning(messages)
        result = db.execute(stmt)
        message_row = result.fetchone()
        
        # Update conversation LAST_MESSAGE_AT
        stmt = update(conversations).where(
            conversations.c.ID == conversation_id
        ).values(
            LAST_MESSAGE_AT=now,
            UPDATED_AT=now
        )
        db.execute(stmt)
        
        db.commit()
        return MessageOut(**dict(message_row._mapping))
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid message data: {str(e)}"
        )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessageListResponse,
    summary="Get conversation messages",
    description="List messages in a conversation with pagination"
)
def list_messages(
    conversation_id: int,
    before_id: Optional[int] = Query(None, description="Get messages before this ID"),
    after_id: Optional[int] = Query(None, description="Get messages after this ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return"),
    visibility: Optional[str] = Query(None, description="Filter by visibility (public/internal)"),
    is_staff: bool = Query(False, description="Is user staff (to see internal messages)"),
    db: Session = Depends(get_db)
):
    """
    Get messages from a conversation.
    Non-staff users only see public messages.
    """
    # Verify conversation exists
    stmt = select(conversations).where(conversations.c.ID == conversation_id)
    result = db.execute(stmt)
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Build query
    query = select(messages).where(
        and_(
            messages.c.CONVERSATION_ID == conversation_id,
            messages.c.DELETED_AT.is_(None)
        )
    )
    
    # Apply visibility filter
    if not is_staff:
        query = query.where(messages.c.VISIBILITY == 'public')
    elif visibility:
        query = query.where(messages.c.VISIBILITY == visibility)
    
    # Apply cursor pagination
    if before_id:
        query = query.where(messages.c.ID < before_id)
    if after_id:
        query = query.where(messages.c.ID > after_id)
    
    # Order and limit
    query = query.order_by(messages.c.CREATED_AT.asc()).limit(limit + 1)
    
    # Execute
    result = db.execute(query)
    rows = result.fetchall()
    
    has_more = len(rows) > limit
    items = [MessageOut(**dict(row._mapping)) for row in rows[:limit]]
    
    return MessageListResponse(
        items=items,
        total=len(items),
        has_more=has_more
    )


@router.get(
    "/messages/{message_id}",
    response_model=MessageOut,
    summary="Get message by ID",
    description="Get a single message"
)
def get_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Get a single message by ID."""
    stmt = select(messages).where(messages.c.ID == message_id)
    result = db.execute(stmt)
    row = result.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found"
        )
    
    return MessageOut(**dict(row._mapping))


@router.patch(
    "/messages/{message_id}",
    response_model=MessageOut,
    summary="Update message",
    description="Edit message body or visibility"
)
def update_message(
    message_id: int,
    message_update: MessageUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a message.
    Sets IS_EDITED=true and UPDATED_AT.
    """
    stmt = select(messages).where(messages.c.ID == message_id)
    result = db.execute(stmt)
    current_message = result.fetchone()
    
    if not current_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found"
        )
    
    update_dict = {}
    if message_update.body is not None:
        update_dict["BODY"] = message_update.body
        update_dict["IS_EDITED"] = True
    if message_update.visibility is not None:
        update_dict["VISIBILITY"] = message_update.visibility
    
    if update_dict:
        update_dict["UPDATED_AT"] = datetime.now(timezone.utc)
        stmt = update(messages).where(
            messages.c.ID == message_id
        ).values(**update_dict).returning(messages)
        result = db.execute(stmt)
        updated_row = result.fetchone()
        db.commit()
        return MessageOut(**dict(updated_row._mapping))
    else:
        return MessageOut(**dict(current_message._mapping))


@router.delete(
    "/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete message",
    description="Soft delete a message"
)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete a message by setting DELETED_AT.
    """
    stmt = select(messages).where(messages.c.ID == message_id)
    result = db.execute(stmt)
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found"
        )
    
    stmt = update(messages).where(
        messages.c.ID == message_id
    ).values(DELETED_AT=datetime.now(timezone.utc))
    db.execute(stmt)
    db.commit()


# ============================================================================
# Participant Endpoints
# ============================================================================

@router.get(
    "/conversations/{conversation_id}/participants",
    response_model=List[ParticipantOut],
    summary="Get conversation participants",
    description="List all participants in a conversation"
)
def list_participants(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get all participants in a conversation."""
    stmt = select(conversation_participants).where(
        conversation_participants.c.CONVERSATION_ID == conversation_id
    ).order_by(conversation_participants.c.JOINED_AT.asc())
    result = db.execute(stmt)
    return [ParticipantOut(**dict(row._mapping)) for row in result.fetchall()]


@router.post(
    "/conversations/{conversation_id}/participants",
    response_model=ParticipantOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add participant",
    description="Add a user to a conversation"
)
def add_participant(
    conversation_id: int,
    participant_data: ParticipantAdd,
    db: Session = Depends(get_db)
):
    """
    Add a participant to a conversation.
    Uses upsert logic to handle duplicates.
    """
    # Verify conversation exists
    stmt = select(conversations).where(conversations.c.ID == conversation_id)
    result = db.execute(stmt)
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Verify user exists
    stmt = select(users).where(users.c.ID == participant_data.user_id)
    result = db.execute(stmt)
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {participant_data.user_id} not found"
        )
    
    try:
        now = datetime.now(timezone.utc)
        stmt = insert(conversation_participants).values(
            CONVERSATION_ID=conversation_id,
            USER_ID=participant_data.user_id,
            ROLE=participant_data.role,
            JOINED_AT=now,
            IS_ACTIVE=True
        ).returning(conversation_participants)
        result = db.execute(stmt)
        row = result.fetchone()
        db.commit()
        return ParticipantOut(**dict(row._mapping))
    except IntegrityError:
        # Participant already exists, return existing
        db.rollback()
        stmt = select(conversation_participants).where(
            and_(
                conversation_participants.c.CONVERSATION_ID == conversation_id,
                conversation_participants.c.USER_ID == participant_data.user_id,
                conversation_participants.c.ROLE == participant_data.role
            )
        )
        result = db.execute(stmt)
        row = result.fetchone()
        return ParticipantOut(**dict(row._mapping))


@router.delete(
    "/conversations/{conversation_id}/participants/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove participant",
    description="Remove a user from a conversation"
)
def remove_participant(
    conversation_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove a participant from a conversation.
    Sets IS_ACTIVE=false and LEFT_AT timestamp.
    """
    stmt = update(conversation_participants).where(
        and_(
            conversation_participants.c.CONVERSATION_ID == conversation_id,
            conversation_participants.c.USER_ID == user_id
        )
    ).values(
        IS_ACTIVE=False,
        LEFT_AT=datetime.now(timezone.utc)
    )
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    db.commit()


# ============================================================================
# Tag Endpoints
# ============================================================================

@router.get(
    "/conversations/{conversation_id}/tags",
    response_model=List[TagOut],
    summary="Get conversation tags",
    description="List all tags for a conversation"
)
def list_tags(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get all tags for a conversation."""
    stmt = select(conversation_tags).where(
        conversation_tags.c.CONVERSATION_ID == conversation_id
    ).order_by(conversation_tags.c.ADDED_AT.asc())
    result = db.execute(stmt)
    return [TagOut(**dict(row._mapping)) for row in result.fetchall()]


@router.post(
    "/conversations/{conversation_id}/tags",
    response_model=TagOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add tag",
    description="Add a tag to a conversation"
)
def add_tag(
    conversation_id: int,
    tag_data: TagCreate,
    db: Session = Depends(get_db)
):
    """Add a tag to a conversation."""
    # Verify conversation exists
    stmt = select(conversations).where(conversations.c.ID == conversation_id)
    result = db.execute(stmt)
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    try:
        stmt = insert(conversation_tags).values(
            CONVERSATION_ID=conversation_id,
            TAG=tag_data.tag.lower(),
            ADDED_BY_USER_ID=tag_data.added_by_user_id,
            ADDED_AT=datetime.now(timezone.utc)
        ).returning(conversation_tags)
        result = db.execute(stmt)
        row = result.fetchone()
        db.commit()
        return TagOut(**dict(row._mapping))
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag already exists for this conversation"
        )


@router.delete(
    "/conversations/{conversation_id}/tags/{tag}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove tag",
    description="Remove a tag from a conversation"
)
def remove_tag(
    conversation_id: int,
    tag: str,
    db: Session = Depends(get_db)
):
    """Remove a tag from a conversation."""
    stmt = delete(conversation_tags).where(
        and_(
            conversation_tags.c.CONVERSATION_ID == conversation_id,
            conversation_tags.c.TAG == tag.lower()
        )
    )
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    db.commit()


# ============================================================================
# Attachment Endpoints
# ============================================================================

@router.post(
    "/messages/{message_id}/attachments",
    response_model=AttachmentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add attachment",
    description="Add a file attachment to a message"
)
def add_attachment(
    message_id: int,
    attachment_data: AttachmentCreate,
    db: Session = Depends(get_db)
):
    """Add an attachment to a message."""
    # Verify message exists
    stmt = select(messages).where(messages.c.ID == message_id)
    result = db.execute(stmt)
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found"
        )
    
    try:
        stmt = insert(message_attachments).values(
            MESSAGE_ID=message_id,
            FILE_NAME=attachment_data.file_name,
            FILE_PATH=attachment_data.file_path,
            FILE_SIZE=attachment_data.file_size,
            MIME_TYPE=attachment_data.mime_type,
            UPLOADED_BY_USER_ID=attachment_data.uploaded_by_user_id,
            UPLOADED_AT=datetime.now(timezone.utc),
            METADATA=attachment_data.metadata
        ).returning(message_attachments)
        result = db.execute(stmt)
        row = result.fetchone()
        db.commit()
        return AttachmentOut(**dict(row._mapping))
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid attachment data: {str(e)}"
        )


@router.get(
    "/messages/{message_id}/attachments",
    response_model=List[AttachmentOut],
    summary="Get message attachments",
    description="List all attachments for a message"
)
def list_attachments(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Get all attachments for a message."""
    stmt = select(message_attachments).where(
        message_attachments.c.MESSAGE_ID == message_id
    ).order_by(message_attachments.c.UPLOADED_AT.asc())
    result = db.execute(stmt)
    return [AttachmentOut(**dict(row._mapping)) for row in result.fetchall()]


# ============================================================================
# Read Receipt Endpoints
# ============================================================================

@router.post(
    "/messages/{message_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark message as read",
    description="Record that a user has read a message (idempotent)"
)
def mark_message_read(
    message_id: int,
    receipt_data: ReadReceiptCreate,
    db: Session = Depends(get_db)
):
    """
    Mark a message as read by a user.
    Idempotent - won't fail if already exists.
    """
    # Verify message exists
    stmt = select(messages).where(messages.c.ID == message_id)
    result = db.execute(stmt)
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found"
        )
    
    read_at = receipt_data.read_at or datetime.now(timezone.utc)
    
    try:
        stmt = insert(read_receipts).values(
            MESSAGE_ID=message_id,
            USER_ID=receipt_data.user_id,
            READ_AT=read_at
        )
        db.execute(stmt)
        db.commit()
    except IntegrityError:
        # Already marked as read, ignore
        db.rollback()


@router.get(
    "/messages/{message_id}/reads",
    response_model=List[ReadReceiptOut],
    summary="Get read receipts",
    description="Get all users who have read a message"
)
def get_read_receipts(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Get all read receipts for a message."""
    stmt = select(read_receipts).where(
        read_receipts.c.MESSAGE_ID == message_id
    ).order_by(read_receipts.c.READ_AT.asc())
    result = db.execute(stmt)
    return [ReadReceiptOut(**dict(row._mapping)) for row in result.fetchall()]


@router.get(
    "/conversations/{conversation_id}/unread-count",
    response_model=UnreadCount,
    summary="Get unread message count",
    description="Get count of unread messages for a user in a conversation"
)
def get_unread_count(
    conversation_id: int,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Get unread message count for a user in a conversation."""
    # Count messages without read receipts
    stmt = select(func.count(messages.c.ID)).where(
        and_(
            messages.c.CONVERSATION_ID == conversation_id,
            messages.c.DELETED_AT.is_(None),
            ~messages.c.ID.in_(
                select(read_receipts.c.MESSAGE_ID).where(
                    read_receipts.c.USER_ID == user_id
                )
            )
        )
    )
    count = db.execute(stmt).scalar()
    
    return UnreadCount(
        conversation_id=conversation_id,
        unread_count=count or 0
    )


@router.get(
    "/unread-summary",
    response_model=UnreadSummary,
    summary="Get unread summary",
    description="Get unread message counts across all conversations for a user"
)
def get_unread_summary(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Get unread counts for all conversations where user is a participant."""
    # Get conversations where user is a participant
    participant_convs = select(conversation_participants.c.CONVERSATION_ID).where(
        and_(
            conversation_participants.c.USER_ID == user_id,
            conversation_participants.c.IS_ACTIVE == True
        )
    )
    
    # Count unread per conversation
    stmt = select(
        messages.c.CONVERSATION_ID,
        func.count(messages.c.ID).label('unread_count')
    ).where(
        and_(
            messages.c.CONVERSATION_ID.in_(participant_convs),
            messages.c.DELETED_AT.is_(None),
            ~messages.c.ID.in_(
                select(read_receipts.c.MESSAGE_ID).where(
                    read_receipts.c.USER_ID == user_id
                )
            )
        )
    ).group_by(messages.c.CONVERSATION_ID)
    
    result = db.execute(stmt)
    items = [
        UnreadCount(conversation_id=row.CONVERSATION_ID, unread_count=row.unread_count)
        for row in result.fetchall()
    ]
    
    total_unread = sum(item.unread_count for item in items)
    
    return UnreadSummary(
        items=items,
        total_unread=total_unread
    )


# ============================================================================
# Reaction Endpoints
# ============================================================================

@router.get(
    "/messages/{message_id}/reactions",
    response_model=List[ReactionSummary],
    summary="Get message reactions",
    description="Get aggregated reactions for a message"
)
def get_reactions(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Get reactions for a message, grouped by emoji."""
    stmt = select(
        message_reactions.c.EMOJI,
        func.count(message_reactions.c.USER_ID).label('count'),
        func.array_agg(message_reactions.c.USER_ID).label('user_ids')
    ).where(
        message_reactions.c.MESSAGE_ID == message_id
    ).group_by(message_reactions.c.EMOJI)
    
    result = db.execute(stmt)
    return [
        ReactionSummary(
            emoji=row.EMOJI,
            count=row.count,
            user_ids=row.user_ids or []
        )
        for row in result.fetchall()
    ]


@router.post(
    "/messages/{message_id}/reactions",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Add reaction",
    description="Add an emoji reaction to a message (idempotent)"
)
def add_reaction(
    message_id: int,
    reaction_data: ReactionCreate,
    db: Session = Depends(get_db)
):
    """
    Add a reaction to a message.
    Idempotent - won't fail if reaction already exists.
    """
    # Verify message exists
    stmt = select(messages).where(messages.c.ID == message_id)
    result = db.execute(stmt)
    if not result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found"
        )
    
    try:
        stmt = insert(message_reactions).values(
            MESSAGE_ID=message_id,
            USER_ID=reaction_data.user_id,
            EMOJI=reaction_data.emoji,
            CREATED_AT=datetime.now(timezone.utc)
        )
        db.execute(stmt)
        db.commit()
    except IntegrityError:
        # Reaction already exists, ignore
        db.rollback()


@router.delete(
    "/messages/{message_id}/reactions",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove reaction",
    description="Remove an emoji reaction from a message"
)
def remove_reaction(
    message_id: int,
    reaction_data: ReactionDelete,
    db: Session = Depends(get_db)
):
    """Remove a reaction from a message."""
    stmt = delete(message_reactions).where(
        and_(
            message_reactions.c.MESSAGE_ID == message_id,
            message_reactions.c.USER_ID == reaction_data.user_id,
            message_reactions.c.EMOJI == reaction_data.emoji
        )
    )
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )
    db.commit()


# ============================================================================
# Assignment Endpoints
# ============================================================================

@router.get(
    "/conversations/{conversation_id}/assignments",
    response_model=List[AssignmentOut],
    summary="Get assignment history",
    description="Get chronological history of conversation assignments"
)
def get_assignment_history(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get assignment history for a conversation."""
    stmt = select(assignment_history).where(
        assignment_history.c.CONVERSATION_ID == conversation_id
    ).order_by(assignment_history.c.ASSIGNED_AT.desc())
    result = db.execute(stmt)
    return [AssignmentOut(**dict(row._mapping)) for row in result.fetchall()]


@router.post(
    "/conversations/{conversation_id}/assignments",
    response_model=ConversationOut,
    summary="Assign conversation",
    description="Assign or reassign a conversation to a user"
)
def assign_conversation(
    conversation_id: int,
    assignment_data: AssignmentCreate,
    current_user_id: int = Query(..., description="Current user ID"),
    db: Session = Depends(get_db)
):
    """
    Assign or reassign a conversation.
    Updates conversation and records in assignment history.
    """
    # Get current conversation
    stmt = select(conversations).where(conversations.c.ID == conversation_id)
    result = db.execute(stmt)
    current_conv = result.fetchone()
    
    if not current_conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    old_assigned_to = current_conv.ASSIGNED_TO_USER_ID
    new_assigned_to = assignment_data.assigned_to_user_id
    
    # Update conversation
    now = datetime.now(timezone.utc)
    stmt = update(conversations).where(
        conversations.c.ID == conversation_id
    ).values(
        ASSIGNED_TO_USER_ID=new_assigned_to,
        UPDATED_AT=now
    ).returning(conversations)
    result = db.execute(stmt)
    updated_conv = result.fetchone()
    
    # Record assignment history
    stmt = insert(assignment_history).values(
        CONVERSATION_ID=conversation_id,
        ASSIGNED_FROM_USER_ID=old_assigned_to,
        ASSIGNED_TO_USER_ID=new_assigned_to,
        ASSIGNED_BY_USER_ID=current_user_id,
        ASSIGNED_AT=now,
        NOTE=assignment_data.note
    )
    db.execute(stmt)
    
    db.commit()
    return ConversationOut(**dict(updated_conv._mapping))

