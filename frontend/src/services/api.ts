/**
 * API Client for UKNF Report Desk Backend
 * Connects to auth-service (8001) and communication-service (8002)
 */

import axios, { AxiosInstance } from 'axios';
import type {
  Report,
  ReportListItem,
  PaginatedResponse,
  Conversation,
  Message,
  Subject,
  DashboardStats,
  StatusCount,
} from '../types';

// ============================================================================
// Base API Client
// ============================================================================

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth interceptor
    this.client.interceptors.request.use((config) => {
      const sessionId = localStorage.getItem('sessionId');
      if (sessionId) {
        config.headers.Authorization = `Bearer ${sessionId}`;
      }
      return config;
    });

    // Add response error handler
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear session and redirect to login
          localStorage.removeItem('sessionId');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  get<T>(url: string, params?: any): Promise<T> {
    return this.client.get(url, { params }).then((res) => res.data);
  }

  post<T>(url: string, data?: any): Promise<T> {
    return this.client.post(url, data).then((res) => res.data);
  }

  put<T>(url: string, data?: any): Promise<T> {
    return this.client.put(url, data).then((res) => res.data);
  }

  patch<T>(url: string, data?: any): Promise<T> {
    return this.client.patch(url, data).then((res) => res.data);
  }

  delete(url: string): Promise<void> {
    return this.client.delete(url).then((res) => res.data);
  }
}

// ============================================================================
// Auth Service API (port 8001)
// ============================================================================

class AuthAPI extends ApiClient {
  constructor() {
    super('/auth');
  }

  async login(email: string, password: string) {
    return this.post<{ session_id: string; expires_in: number }>('/authn', {
      email,
      password,
    });
  }

  async register(data: {
    email: string;
    password: string;
    user_name?: string;
    user_lastname?: string;
  }) {
    return this.post('/register', data);
  }

  async logout(sessionId: string) {
    return this.post('/logout', { session_id: sessionId });
  }

  async checkAuthorization(sessionId: string, resourceId: string) {
    return this.post<{ authorized: boolean; message: string }>('/authz', {
      session_id: sessionId,
      resource_id: resourceId,
    });
  }

  async getMe(sessionId: string) {
    return this.get<{
      user_id: number;
      email: string;
      firstName: string | null;
      lastName: string | null;
      phone: string | null;
      isActive: boolean;
      subjectId: number | null;
      subjectName: string | null;
      uknfId: string | null;
    }>('/me', { session_id: sessionId });
  }

  async getUserIdBySession(sessionId: string) {
    return this.get<{ user_id: number; session_id: string }>(
      `/get-user-id-by-session/${sessionId}`
    );
  }
}

// ============================================================================
// Communication Service API (port 8002)
// ============================================================================

class CommunicationAPI extends ApiClient {
  constructor() {
    super('/api');
  }

  // ========================================
  // Reports
  // ========================================

  async getReports(filters?: {
    category?: string;
    archived?: boolean;
    subject_scope?: 'mine' | 'all';
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<ReportListItem>> {
    return this.get('/reporting/reports', filters);
  }

  async getReport(id: number): Promise<Report> {
    return this.get(`/reporting/reports/${id}`);
  }

  async getReportDetails(id: number) {
    return this.get(`/reporting/reports/${id}/details`);
  }

  async getReportsByStatus(): Promise<StatusCount[]> {
    // This would aggregate reports by status
    return this.get('/reporting/reports/stats');
  }

  async getRecentReports(limit: number = 5): Promise<ReportListItem[]> {
    return this.get<PaginatedResponse<ReportListItem>>('/reporting/reports', {
      page: 1,
      page_size: limit,
      archived: false,
    }).then((res) => res.items);
  }

  // ========================================
  // Conversations & Messages
  // ========================================

  async getConversations(filters?: {
    subject_id?: number;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Conversation>> {
    return this.get('/chat/conversations', filters);
  }

  async getConversation(id: number) {
    return this.get(`/chat/conversations/${id}`);
  }

  async getMessages(
    conversationId: number,
    params?: { limit?: number; is_staff?: boolean }
  ): Promise<{ items: Message[]; total: number; has_more: boolean }> {
    return this.get(`/chat/conversations/${conversationId}/messages`, params);
  }

  async sendMessage(conversationId: number, data: {
    sender_user_id: number;
    body: string;
    visibility?: 'public' | 'internal';
  }) {
    return this.post(`/chat/conversations/${conversationId}/messages`, data);
  }

  async getUnreadSummary(userId: number) {
    return this.get('/chat/unread-summary', { user_id: userId });
  }

  // ========================================
  // Subjects
  // ========================================

  async getMySubjects(): Promise<Subject[]> {
    return this.get('/reporting/subjects/mine');
  }

  async getSubject(id: number): Promise<Subject> {
    return this.get(`/subjects/${id}`);
  }

  // ========================================
  // Dashboard Stats
  // ========================================

  async getDashboardStats(): Promise<DashboardStats> {
    // Aggregate multiple endpoints for dashboard
    const [reportsRes, unreadRes] = await Promise.all([
      this.get<PaginatedResponse<ReportListItem>>('/reporting/reports', {
        page: 1,
        page_size: 10,
        archived: false,
      }),
      this.get<{ items: any[]; total_unread: number }>('/chat/unread-summary', {
        user_id: 1, // TODO: Get from auth state
      }),
    ]);

    // Calculate status counts
    const statusCounts: StatusCount[] = [];
    const statusMap = new Map<string, number>();
    
    reportsRes.items.forEach((report) => {
      const current = statusMap.get(report.status) || 0;
      statusMap.set(report.status, current + 1);
    });

    statusMap.forEach((count, status) => {
      statusCounts.push({
        status: status as any,
        count,
        label: '', // Will be filled from backend
      });
    });

    return {
      reports: {
        total: reportsRes.total,
        by_status: statusCounts,
        recent: reportsRes.items.slice(0, 5),
      },
      messages: {
        unread_count: unreadRes.total_unread,
        recent_threads: [],
      },
      cases: {
        open: 0,
        pending: 0,
        resolved: 0,
      },
      notifications: [],
    };
  }
}

// ============================================================================
// Export API instances
// ============================================================================

// ============================================================================
// Administration Service API (port 8000)
// ============================================================================

class AdministrationAPI extends ApiClient {
  constructor() {
    super('/admin');
  }

  // ========================================
  // Subjects
  // ========================================

  async getSubject(id: number): Promise<Subject> {
    return this.get(`/subjects/${id}`);
  }

  async updateSubject(id: number, data: Partial<Subject>): Promise<Subject> {
    return this.put(`/subjects/${id}`, data);
  }

  async getSubjectHistory(id: number): Promise<{
    HISTORY_ID: number;
    OPERATION_TYPE: string;
    MODIFIED_AT: string;
    MODIFIED_BY: number | null;
    ID: number;
    NAME_STRUCTURE: string | null;
    [key: string]: any;
  }[]> {
    return this.get(`/subjects/${id}/history`);
  }

  async getManageableSubjects(): Promise<Subject[]> {
    return this.get('/subjects/manageable');
  }
}

export const authAPI = new AuthAPI();
export const commAPI = new CommunicationAPI();
export const adminAPI = new AdministrationAPI();

