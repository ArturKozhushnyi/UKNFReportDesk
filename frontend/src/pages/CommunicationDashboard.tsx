/**
 * Communication Dashboard
 * Main landing page with reports, messages, cases, notifications, and file repository
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  FileText,
  MessageSquare,
  AlertCircle,
  CheckCircle,
  Clock,
  XCircle,
  ChevronRight,
  Bell,
  Folder,
  TrendingUp,
} from 'lucide-react';
import { commAPI } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import type { DashboardStats, ValidationStatus } from '../types';

// ============================================================================
// Status Badge Component
// ============================================================================

const STATUS_CONFIG: Record<ValidationStatus, { label: string; color: string; icon: React.ReactNode }> = {
  DRAFT: { label: 'Robocze', color: 'bg-gray-100 text-gray-800', icon: <FileText size={14} /> },
  SUBMITTED: { label: 'Przekazane', color: 'bg-blue-100 text-blue-800', icon: <Clock size={14} /> },
  IN_PROGRESS: { label: 'W trakcie', color: 'bg-yellow-100 text-yellow-800', icon: <Clock size={14} /> },
  SUCCESS: { label: 'Zaakceptowane', color: 'bg-green-100 text-green-800', icon: <CheckCircle size={14} /> },
  RULE_ERRORS: { label: 'Błędy walidacji', color: 'bg-red-100 text-red-800', icon: <XCircle size={14} /> },
  TECH_ERROR: { label: 'Błąd techniczny', color: 'bg-red-100 text-red-800', icon: <AlertCircle size={14} /> },
  TIMEOUT: { label: 'Przekroczono czas', color: 'bg-orange-100 text-orange-800', icon: <AlertCircle size={14} /> },
  QUESTIONED_BY_UKNF: { label: 'Zakwestionowane', color: 'bg-purple-100 text-purple-800', icon: <AlertCircle size={14} /> },
};

const StatusBadge: React.FC<{ status: ValidationStatus }> = ({ status }) => {
  const config = STATUS_CONFIG[status];
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
      {config.icon}
      <span className="ml-1">{config.label}</span>
    </span>
  );
};

// ============================================================================
// Reports Snapshot Widget
// ============================================================================

const ReportsSnapshot: React.FC<{ stats: DashboardStats['reports'] }> = ({ stats }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Reports Overview</h2>
        <Link
          to="/communication/reports"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          View All →
        </Link>
      </div>

      {/* Status Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {stats.by_status.map((item) => {
          const config = STATUS_CONFIG[item.status];
          return (
            <div key={item.status} className="text-center p-3 bg-gray-50 rounded-lg">
              <div className={`inline-flex items-center justify-center w-10 h-10 rounded-full ${config.color} mb-2`}>
                {config.icon}
              </div>
              <p className="text-2xl font-bold text-gray-900">{item.count}</p>
              <p className="text-xs text-gray-600">{config.label}</p>
            </div>
          );
        })}
      </div>

      {/* Recent Reports */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Recent Reports</h3>
        <div className="space-y-2">
          {stats.recent.map((report) => (
            <Link
              key={report.report_id}
              to={`/communication/reports/${report.report_id}`}
              className="block p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{report.report_type_name}</p>
                  <p className="text-sm text-gray-600">
                    {report.subject_name} • {report.period_display}
                  </p>
                </div>
                <StatusBadge status={report.status} />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Messages Overview Widget
// ============================================================================

const MessagesOverview: React.FC<{ unreadCount: number }> = ({ unreadCount }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Messages</h2>
        <Link
          to="/communication/messages"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          View All →
        </Link>
      </div>

      <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg mb-4">
        <div className="flex items-center">
          <MessageSquare className="text-blue-600 mr-3" size={24} />
          <div>
            <p className="text-2xl font-bold text-blue-900">{unreadCount}</p>
            <p className="text-sm text-blue-700">Unread Messages</p>
          </div>
        </div>
        <ChevronRight className="text-blue-400" size={24} />
      </div>

      <div className="space-y-2">
        <p className="text-sm text-gray-600">Quick Actions:</p>
        <div className="grid grid-cols-2 gap-2">
          <Link
            to="/communication/messages/compose"
            className="px-4 py-2 text-sm font-medium text-center text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            New Message
          </Link>
          <Link
            to="/communication/messages?filter=unread"
            className="px-4 py-2 text-sm font-medium text-center text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Unread Only
          </Link>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Cases Overview Widget
// ============================================================================

const CasesOverview: React.FC<{ cases: { open: number; pending: number; resolved: number } }> = ({ cases }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Cases</h2>
        <Link
          to="/communication/cases"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          View All →
        </Link>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <CheckCircle className="mx-auto mb-2 text-green-600" size={24} />
          <p className="text-2xl font-bold text-gray-900">{cases.open}</p>
          <p className="text-xs text-gray-600">Open</p>
        </div>
        <div className="text-center p-4 bg-yellow-50 rounded-lg">
          <Clock className="mx-auto mb-2 text-yellow-600" size={24} />
          <p className="text-2xl font-bold text-gray-900">{cases.pending}</p>
          <p className="text-xs text-gray-600">Pending</p>
        </div>
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <CheckCircle className="mx-auto mb-2 text-blue-600" size={24} />
          <p className="text-2xl font-bold text-gray-900">{cases.resolved}</p>
          <p className="text-xs text-gray-600">Resolved</p>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Notifications Widget
// ============================================================================

const NotificationsFeed: React.FC<{ notifications: any[] }> = ({ notifications }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Notifications</h2>
        <Bell className="text-gray-400" size={20} />
      </div>

      {notifications.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Bell className="mx-auto mb-2 text-gray-300" size={48} />
          <p className="text-sm">No new notifications</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.slice(0, 5).map((notification, index) => (
            <div key={index} className="p-3 border border-gray-200 rounded-lg">
              <p className="text-sm font-medium text-gray-900">{notification.title}</p>
              <p className="text-xs text-gray-600 mt-1">{notification.message}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// File Repository Widget
// ============================================================================

const FileRepositoryQuickAccess: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">File Repository</h2>
        <Link
          to="/communication/library"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          Browse All →
        </Link>
      </div>

      <div className="space-y-3">
        <div className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
          <Folder className="text-blue-600 mr-3" size={20} />
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">Report Templates</p>
            <p className="text-xs text-gray-500">12 files</p>
          </div>
        </div>
        
        <div className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
          <Folder className="text-green-600 mr-3" size={20} />
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">Submitted Reports</p>
            <p className="text-xs text-gray-500">45 files</p>
          </div>
        </div>
        
        <div className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
          <Folder className="text-purple-600 mr-3" size={20} />
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">Validation Results</p>
            <p className="text-xs text-gray-500">38 files</p>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <input
          type="text"
          placeholder="Search files..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
};

// ============================================================================
// Bulletin Board Widget
// ============================================================================

const BulletinBoard: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Bulletin Board</h2>
        <TrendingUp className="text-gray-400" size={20} />
      </div>

      <div className="space-y-3">
        <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
          <p className="text-sm font-medium text-blue-900">New Reporting Period Open</p>
          <p className="text-xs text-blue-700 mt-1">Q1 2025 reporting period is now open for submissions</p>
          <p className="text-xs text-blue-600 mt-2">Posted: 2025-01-02</p>
        </div>

        <div className="p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
          <p className="text-sm font-medium text-yellow-900">System Maintenance</p>
          <p className="text-xs text-yellow-700 mt-1">Planned maintenance on Saturday, 10:00-12:00</p>
          <p className="text-xs text-yellow-600 mt-2">Posted: 2025-01-05</p>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Main Dashboard Component
// ============================================================================

export const CommunicationDashboard: React.FC = () => {
  const { user, role } = useAuthStore();
  
  const { data: stats, isLoading, error } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: () => commAPI.getDashboardStats(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <AlertCircle className="text-red-600 mb-2" size={24} />
        <p className="text-red-900 font-medium">Failed to load dashboard</p>
        <p className="text-red-700 text-sm mt-1">{(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Welcome, {user?.USER_NAME} {user?.USER_LASTNAME}
        </h1>
        <p className="text-blue-100">
          {role === 'administrator' && 'Administrator Dashboard - Full System Access'}
          {role === 'internal_user' && 'UKNF Staff Dashboard - Manage Reports and Communications'}
          {role === 'external_user' && 'Entity Dashboard - Submit and Track Your Reports'}
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Reports</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.reports.total || 0}</p>
            </div>
            <FileText className="text-blue-600" size={40} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Unread Messages</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.messages.unread_count || 0}</p>
            </div>
            <MessageSquare className="text-green-600" size={40} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Open Cases</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.cases.open || 0}</p>
            </div>
            <AlertCircle className="text-yellow-600" size={40} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Notifications</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.notifications.length || 0}</p>
            </div>
            <Bell className="text-purple-600" size={40} />
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {stats && <ReportsSnapshot stats={stats.reports} />}
          {stats && <MessagesOverview unreadCount={stats.messages.unread_count} />}
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {stats && <CasesOverview cases={stats.cases} />}
          {stats && <NotificationsFeed notifications={stats.notifications} />}
          <BulletinBoard />
        </div>
      </div>

      {/* File Repository Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <FileRepositoryQuickAccess />
        </div>
        
        {/* Quick Links */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Links</h3>
          <div className="space-y-2">
            <Link
              to="/communication/reports/new"
              className="block px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center font-medium"
            >
              Submit New Report
            </Link>
            <Link
              to="/communication/cases/new"
              className="block px-4 py-3 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors text-center font-medium"
            >
              Open New Case
            </Link>
            <Link
              to="/communication/library"
              className="block px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-center font-medium"
            >
              Browse Library
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

