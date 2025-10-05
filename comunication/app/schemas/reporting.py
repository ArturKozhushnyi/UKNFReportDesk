"""
Pydantic schemas for UKNF Reporting System
"""
from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Enums and Types
# ============================================================================

ReportCategory = Literal['quarterly', 'annual', 'other']
PeriodType = Literal['quarterly', 'annual', 'other']
ValidationStatus = Literal['DRAFT', 'SUBMITTED', 'IN_PROGRESS', 'SUCCESS', 'RULE_ERRORS', 'TECH_ERROR', 'TIMEOUT', 'QUESTIONED_BY_UKNF']
ErrorSeverity = Literal['error', 'warning']
ExpectedStatus = Literal['expected', 'waived']
ReminderStatus = Literal['scheduled', 'sent', 'cancelled']
SubjectScope = Literal['mine', 'all']


# ============================================================================
# Status Dictionary Schemas
# ============================================================================

class ReportStatusOut(BaseModel):
    """Status from dictionary with meaning"""
    CODE: str
    LABEL: str
    ORDER_NUM: int
    FINAL: bool
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Report Type Schemas
# ============================================================================

class ReportTypeOut(BaseModel):
    ID: int
    CODE: str
    NAME: str
    CATEGORY: ReportCategory
    
    model_config = ConfigDict(from_attributes=True)


class ReportTemplateOut(BaseModel):
    ID: int
    REPORT_TYPE_ID: int
    VERSION: str
    STORAGE_URL: str
    ACTIVE_FROM: Optional[date] = None
    ACTIVE_TO: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Period Schemas
# ============================================================================

class PeriodSpec(BaseModel):
    """Period specification for queries/creation"""
    period_type: PeriodType
    year: int
    quarter: Optional[int] = Field(None, ge=1, le=4)
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period_type": "quarterly",
            "year": 2025,
            "quarter": 1
        }
    })


class ReportingPeriodOut(BaseModel):
    ID: int
    PERIOD_TYPE: PeriodType
    YEAR: int
    QUARTER: Optional[int] = None
    START_DATE: date
    END_DATE: date
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Report Creation Schemas
# ============================================================================

class ReportCreate(BaseModel):
    subject_id: int
    report_type_code: str
    period: PeriodSpec
    created_by_user_id: int
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "subject_id": 1,
            "report_type_code": "RIP",
            "period": {
                "period_type": "quarterly",
                "year": 2025,
                "quarter": 1
            },
            "created_by_user_id": 5
        }
    })


class ReportFileUpload(BaseModel):
    original_file_name: str = Field(..., min_length=1, max_length=500)
    mime_type: str = Field(default='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    size_bytes: Optional[int] = None
    storage_url: str = Field(..., min_length=1, max_length=2000)
    uploaded_by_user_id: int
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "original_file_name": "RIP100000_Q1_2025.xlsx",
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": 524288,
            "storage_url": "/storage/reports/2025/Q1/abc123.xlsx",
            "uploaded_by_user_id": 5
        }
    })


# ============================================================================
# Report Output Schemas
# ============================================================================

class ReportOut(BaseModel):
    ID: int
    SUBJECT_ID: int
    REPORT_TYPE_ID: int
    PERIOD_ID: int
    CREATED_BY_USER_ID: int
    CURRENT_STATUS: ValidationStatus
    HAS_CORRECTION: bool
    IS_ARCHIVED: bool
    ARCHIVED_AT: Optional[datetime] = None
    DATE_CREATE: datetime
    DATE_ACTUALIZATION: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ReportFileOut(BaseModel):
    ID: int
    REPORT_ID: int
    VERSION_NO: int
    UPLOADED_BY_USER_ID: int
    ORIGINAL_FILE_NAME: str
    MIME_TYPE: str
    SIZE_BYTES: Optional[int] = None
    STORAGE_URL: str
    UPLOADED_AT: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ValidationRunOut(BaseModel):
    ID: int
    REPORT_FILE_ID: int
    EXTERNAL_JOB_ID: Optional[str] = None
    STATUS: ValidationStatus
    METADATA: Optional[dict] = None
    REPORT_LINK_URL: Optional[str] = None
    STARTED_AT: datetime
    FINISHED_AT: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ValidationErrorOut(BaseModel):
    ID: int
    VALIDATION_RUN_ID: int
    RULE_CODE: Optional[str] = None
    SEVERITY: ErrorSeverity
    MESSAGE: str
    SHEET: Optional[str] = None
    ROW_NUM: Optional[int] = None
    COLUMN_NAME: Optional[str] = None
    CELL_REF: Optional[str] = None
    CONTEXT: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)


class ReportStatusHistoryOut(BaseModel):
    ID: int
    REPORT_ID: int
    STATUS_CODE: ValidationStatus
    CHANGED_AT: datetime
    CHANGED_BY_USER_ID: Optional[int] = None
    NOTE: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Detailed Report Card
# ============================================================================

class ReportDetail(BaseModel):
    """Complete report card with all details"""
    report: ReportOut
    status_info: ReportStatusOut
    report_type: ReportTypeOut
    period: ReportingPeriodOut
    subject_name: Optional[str] = None
    created_by_name: Optional[str] = None
    files: List[ReportFileOut] = []
    latest_validation: Optional[ValidationRunOut] = None
    conversations: List[int] = []  # conversation IDs


class ReportFileUploadResponse(BaseModel):
    """Response after file upload"""
    report_file_id: int
    validation_run_id: int
    status: str = "SUBMITTED"
    message: str = "Validation started"


# ============================================================================
# Validator Callback Schema
# ============================================================================

class ValidationErrorCallback(BaseModel):
    rule_code: Optional[str] = None
    severity: ErrorSeverity
    message: str
    sheet: Optional[str] = None
    row_num: Optional[int] = None
    column_name: Optional[str] = None
    cell_ref: Optional[str] = None
    context: Optional[dict] = None


class ValidatorCallback(BaseModel):
    """Webhook payload from external validator"""
    external_job_id: Optional[str] = None
    report_file_id: Optional[int] = None
    status: ValidationStatus
    report_link_url: Optional[str] = None
    metadata: Optional[dict] = None
    errors: Optional[List[ValidationErrorCallback]] = None
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "external_job_id": "VAL-2025-001-ABC123",
            "report_file_id": 42,
            "status": "SUCCESS",
            "report_link_url": "https://validator.uknf.gov.pl/reports/2025/Q1/abc123.pdf",
            "metadata": {
                "uknf_id": "UKNF001",
                "validated_at": "2025-10-05T12:00:00Z"
            }
        }
    })


# ============================================================================
# Calendar & Reminders
# ============================================================================

class ExpectedReportOut(BaseModel):
    ID: int
    SUBJECT_ID: int
    REPORT_TYPE_ID: int
    PERIOD_ID: int
    DUE_AT: datetime
    STATUS: ExpectedStatus
    DATE_CREATE: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CalendarEntry(BaseModel):
    """Calendar entry with progress"""
    expected_report: ExpectedReportOut
    subject_name: str
    report_type_code: str
    report_type_name: str
    period_display: str
    submitted: bool
    report_id: Optional[int] = None
    current_status: Optional[ValidationStatus] = None


class ReminderCreate(BaseModel):
    subject_id: int
    report_type_id: Optional[int] = None
    report_type_code: Optional[str] = None
    period_id: int
    remind_at: datetime
    created_by_user_id: int
    payload: Optional[dict] = None
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "subject_id": 1,
            "report_type_code": "RIP",
            "period_id": 5,
            "remind_at": "2025-01-27T09:00:00Z",
            "created_by_user_id": 3,
            "payload": {
                "template": "deadline_reminder",
                "days_before": 3
            }
        }
    })


class ReminderOut(BaseModel):
    ID: int
    SUBJECT_ID: int
    REPORT_TYPE_ID: int
    PERIOD_ID: int
    REMIND_AT: datetime
    CREATED_BY_USER_ID: Optional[int] = None
    STATUS: ReminderStatus
    PAYLOAD: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Archive & Linking
# ============================================================================

class ArchiveUpdate(BaseModel):
    is_archived: bool


class ConversationLink(BaseModel):
    conversation_id: int


class ReportConversationOut(BaseModel):
    ID: int
    REPORT_ID: int
    CONVERSATION_ID: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# List/Search Responses
# ============================================================================

class ReportListItem(BaseModel):
    """Tabular view for report registers"""
    report_id: int
    report_type_name: str
    report_type_code: str
    period_display: str
    subject_name: str
    status: ValidationStatus
    status_label: str
    date_create: datetime
    submitted_by_name: str
    submitted_by_email: Optional[str] = None
    submitted_by_phone: Optional[str] = None
    has_correction: bool
    is_archived: bool


class ReportListResponse(BaseModel):
    items: List[ReportListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class ValidationErrorListResponse(BaseModel):
    items: List[ValidationErrorOut]
    total: int
    page: int
    page_size: int


class NonFilerEntry(BaseModel):
    """Subject that hasn't filed a required report"""
    subject_id: int
    subject_name: str
    subject_code: Optional[str] = None
    subject_email: Optional[str] = None
    subject_phone: Optional[str] = None
    report_type: str
    period_display: str
    due_at: datetime
    days_overdue: int


class NonFilerNotifyRequest(BaseModel):
    """Request to send notifications to non-filers"""
    period_id: Optional[int] = None
    period_spec: Optional[PeriodSpec] = None
    report_type_code: str
    subject_ids: List[int]
    conversation_template: Optional[dict] = None
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period_spec": {
                "period_type": "quarterly",
                "year": 2025,
                "quarter": 1
            },
            "report_type_code": "RIP",
            "subject_ids": [1, 5, 8],
            "conversation_template": {
                "title": "Report Q1 2025 - Missing Submission",
                "message": "Your quarterly report for Q1 2025 is overdue. Please submit as soon as possible."
            }
        }
    })


# ============================================================================
# Status Summary for Chat
# ============================================================================

class ReportStatusSummary(BaseModel):
    """Formatted status for chat messages"""
    report_id: int
    status_code: ValidationStatus
    status_label: str
    status_meaning: str
    is_final: bool
    report_link_url: Optional[str] = None
    has_errors: bool
    error_count: int
    warning_count: int
    next_actions: List[str]
    metadata: dict

