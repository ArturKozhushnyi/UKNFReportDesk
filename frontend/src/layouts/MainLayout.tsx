/**
 * Main Application Layout
 * Includes navigation, breadcrumbs, and role-based menu
 */

import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  FileText,
  Shield,
  Settings,
  Users,
  Building2,
  LogOut,
  Menu,
  X,
  Home,
  ChevronRight,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import type { UserRole } from '../types';

interface MenuItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  roles?: UserRole[];
  children?: MenuItem[];
}

const MENU_ITEMS: MenuItem[] = [
  {
    label: 'Dashboard',
    path: '/',
    icon: <Home size={20} />,
  },
  {
    label: 'Communication Module',
    path: '/communication',
    icon: <MessageSquare size={20} />,
    children: [
      { label: 'Reports', path: '/communication/reports', icon: <FileText size={18} /> },
      { label: 'Cases', path: '/communication/cases', icon: <MessageSquare size={18} /> },
      { label: 'Messages', path: '/communication/messages', icon: <MessageSquare size={18} /> },
      { label: 'Announcements', path: '/communication/announcements', icon: <MessageSquare size={18} /> },
      { label: 'Library', path: '/communication/library', icon: <FileText size={18} /> },
    ],
  },
  {
    label: 'Authentication & Authorization',
    path: '/auth-module',
    icon: <Shield size={20} />,
    roles: ['internal_user', 'administrator'],
    children: [
      { label: 'Authentication', path: '/auth-module/authentication', icon: <Shield size={18} /> },
      { label: 'Requests', path: '/auth-module/requests', icon: <FileText size={18} /> },
      { label: 'Authorization', path: '/auth-module/authorization', icon: <Shield size={18} /> },
      { label: 'Contact Form', path: '/auth-module/contact', icon: <MessageSquare size={18} /> },
    ],
  },
  {
    label: 'Administrative Module',
    path: '/admin',
    icon: <Settings size={20} />,
    roles: ['internal_user', 'administrator'],
    children: [
      { label: 'Manage Subjects', path: '/manage-subjects', icon: <Building2 size={18} /> },
      { label: 'User Management', path: '/admin/users', icon: <Users size={18} /> },
      { label: 'Password Policy', path: '/admin/password-policy', icon: <Shield size={18} /> },
      { label: 'Roles & Permissions', path: '/admin/roles', icon: <Shield size={18} /> },
      { label: 'Entities Database', path: '/admin/entities', icon: <Building2 size={18} /> },
      { label: 'Entity Data Updater', path: '/admin/entity-updater', icon: <Settings size={18} /> },
    ],
  },
];

const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  
  const pathnames = location.pathname.split('/').filter((x) => x);
  
  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-6">
      <Link to="/" className="hover:text-blue-600 flex items-center">
        <Home size={16} className="mr-1" />
        Home
      </Link>
      {pathnames.map((name, index) => {
        const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;
        const displayName = name.charAt(0).toUpperCase() + name.slice(1).replace(/-/g, ' ');
        
        return (
          <React.Fragment key={routeTo}>
            <ChevronRight size={16} className="text-gray-400" />
            {isLast ? (
              <span className="text-gray-900 font-medium">{displayName}</span>
            ) : (
              <Link to={routeTo} className="hover:text-blue-600">
                {displayName}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

export const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  const { user, role, firstName, lastName, subjectName, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const canAccessMenuItem = (item: MenuItem): boolean => {
    if (!item.roles) return true;
    return role ? item.roles.includes(role) : false;
  };

  const filteredMenuItems = MENU_ITEMS.filter(canAccessMenuItem);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`bg-white border-r border-gray-200 transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-0'
        } overflow-hidden`}
      >
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-blue-900">UKNF Report Desk</h1>
          <p className="text-xs text-gray-500 mt-1">Polish Financial Supervision</p>
        </div>

        <nav className="p-4 space-y-1">
          {filteredMenuItems.map((item) => (
            <div key={item.path}>
              <Link
                to={item.path}
                className="flex items-center px-3 py-2 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-700 transition-colors"
              >
                {item.icon}
                <span className="ml-3 font-medium">{item.label}</span>
              </Link>
              
              {item.children && (
                <div className="ml-6 mt-1 space-y-1">
                  {item.children.filter(canAccessMenuItem).map((child) => (
                    <Link
                      key={child.path}
                      to={child.path}
                      className="flex items-center px-3 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-50 hover:text-gray-900 transition-colors"
                    >
                      {child.icon}
                      <span className="ml-2">{child.label}</span>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100"
            >
              {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {firstName && lastName 
                    ? `${firstName} ${lastName}` 
                    : user?.USER_NAME && user?.USER_LASTNAME
                    ? `${user.USER_NAME} ${user.USER_LASTNAME}`
                    : user?.EMAIL || 'User'}
                </p>
                {subjectName && (
                  <p className="text-xs text-gray-600 mt-0.5">
                    {subjectName}
                  </p>
                )}
                <p className="text-xs text-gray-500 capitalize mt-0.5">
                  {role?.replace('_', ' ')}
                </p>
              </div>
              
              <button
                onClick={handleLogout}
                className="flex items-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <LogOut size={18} className="mr-2" />
                Logout
              </button>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          <Breadcrumbs />
          <Outlet />
        </main>
      </div>
    </div>
  );
};

