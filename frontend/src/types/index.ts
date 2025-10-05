/**
 * Type definitions for UKNF Report Desk
 */

// ============================================================================
// User & Auth Types
// ============================================================================

export type UserRole = 'external_user' | 'internal_user' | 'administrator';

export interface User {
  ID: number;
  USER_NAME: string | null;
  USER_LASTNAME: string | null;
  EMAIL: string;
  PHONE: string | null;
  IS_USER_ACTIVE: boolean;
  PESEL?: string; // Masked
}

export interface AuthState {
  user: User | null;
  sessionId: string | null;
  isAuthenticated: boolean;
  role: UserRole | null;
}

// ============================================================================
// Report Types
// ============================================================================

export type ValidationStatus = 
  | 'DRAFT'
  | 'SUBMITTED'
  | 'IN_PROGRESS'
  | 'SUCCESS'
  | 'RULE_ERRORS'
  | 'TECH_ERROR'
  | 'TIMEOUT'
  | 'QUESTIONED_BY_UKNF';

export type ReportCategory = 'quarterly' | 'annual' | 'other';

export interface Report {
  ID: number;
  SUBJECT_ID: number;
  REPORT_TYPE_ID: number;
  PERIOD_ID: number;
  CREATED_BY_USER_ID: number;
  CURRENT_STATUS: ValidationStatus;
  HAS_CORRECTION: boolean;
  IS_ARCHIVED: boolean;
  ARCHIVED_AT: string | null;
  DATE_CREATE: string;
  DATE_ACTUALIZATION: string | null;
}

export interface ReportListItem {
  report_id: number;
  report_type_name: string;
  report_type_code: string;
  period_display: string;
  subject_name: string;
  status: ValidationStatus;
  status_label: string;
  date_create: string;
  submitted_by_name: string;
  submitted_by_email: string | null;
  submitted_by_phone: string | null;
  has_correction: boolean;
  is_archived: boolean;
}

export interface StatusCount {
  status: ValidationStatus;
  count: number;
  label: string;
}

// ============================================================================
// Conversation/Message Types
// ============================================================================

export type ConversationType = 'support' | 'inquiry' | 'complaint' | 'consultation' | 'report';
export type ConversationStatus = 'open' | 'pending' | 'resolved' | 'closed' | 'archived';
export type MessageVisibility = 'public' | 'internal';

export interface Conversation {
  ID: number;
  SUBJECT_ID: number;
  TYPE: ConversationType;
  STATUS: ConversationStatus;
  PRIORITY: string;
  TITLE: string | null;
  CREATED_BY_USER_ID: number;
  ASSIGNED_TO_USER_ID: number | null;
  CREATED_AT: string;
  UPDATED_AT: string;
  CLOSED_AT: string | null;
  LAST_MESSAGE_AT: string | null;
  METADATA: any;
}

export interface Message {
  ID: number;
  CONVERSATION_ID: number;
  SENDER_USER_ID: number;
  PARENT_MESSAGE_ID: number | null;
  BODY: string;
  VISIBILITY: MessageVisibility;
  MESSAGE_TYPE: string;
  CREATED_AT: string;
  UPDATED_AT: string | null;
  DELETED_AT: string | null;
  IS_EDITED: boolean;
  METADATA: any;
}

export interface MessageThread {
  conversation: Conversation;
  messages: Message[];
  unread_count: number;
  participants: any[];
}

// ============================================================================
// Subject/Entity Types
// ============================================================================

export interface Subject {
  ID: number;
  TYPE_STRUCTURE?: string | null;
  CODE_UKNF?: string | null;
  NAME_STRUCTURE?: string | null;
  LEI?: string | null;
  NIP?: string | null;
  KRS?: string | null;
  STREET?: string | null;
  NR_STRET?: string | null;
  NR_HOUSE?: string | null;
  POST_CODE?: string | null;
  TOWN?: string | null;
  PHONE?: string | null;
  EMAIL?: string | null;
  UKNF_ID?: string | null;
  STATUS_S?: string | null;
  KATEGORY_S?: string | null;
  SELEKTOR_S?: string | null;
  SUBSELEKTOR_S?: string | null;
  TRANS_S?: boolean | null;
  DATE_CREATE?: string | null;
  DATE_ACTRUALIZATION?: string | null;
  VALIDATED?: boolean | null;
  RESOURCE_ID?: string | null;
}

// ============================================================================
// File/Attachment Types
// ============================================================================

export interface Attachment {
  ID: number;
  MESSAGE_ID: number;
  FILE_NAME: string;
  FILE_PATH: string;
  FILE_SIZE: number;
  MIME_TYPE: string;
  UPLOADED_BY_USER_ID: number;
  UPLOADED_AT: string;
}

// ============================================================================
// Notification Types
// ============================================================================

export interface Notification {
  id: number;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  action_url?: string;
}

// ============================================================================
// Dashboard Stats
// ============================================================================

export interface DashboardStats {
  reports: {
    total: number;
    by_status: StatusCount[];
    recent: ReportListItem[];
  };
  messages: {
    unread_count: number;
    recent_threads: MessageThread[];
  };
  cases: {
    open: number;
    pending: number;
    resolved: number;
  };
  notifications: Notification[];
}

// ============================================================================
// API Response Types
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
}

