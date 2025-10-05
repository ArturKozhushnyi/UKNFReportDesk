/**
 * Main Application Component
 * Sets up routing, auth guards, and React Query
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from './layouts/MainLayout';
import { AuthGuard } from './guards/AuthGuard';
import { CommunicationDashboard } from './pages/CommunicationDashboard';
import { LoginPage } from './pages/LoginPage';
import { RegistrationPage } from './pages/RegistrationPage';
import { SubjectManagementPage } from './pages/SubjectManagementPage';
import ManageSubjectsPage from './pages/ManageSubjectsPage';
import { FAQPage } from './pages/FAQPage';
import './styles/index.css';

// Create QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegistrationPage />} />
          
          {/* Protected Routes */}
          <Route element={<AuthGuard><MainLayout /></AuthGuard>}>
            <Route index element={<CommunicationDashboard />} />
            
            {/* Communication Module */}
            <Route path="/communication">
              <Route index element={<Navigate to="/communication/reports" replace />} />
              <Route path="reports" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Reports Registry</h2><p className="text-gray-600 mt-2">Full reports list will be displayed here</p></div>} />
              <Route path="reports/:id" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Report Details</h2></div>} />
              <Route path="cases" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Cases</h2></div>} />
              <Route path="messages" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Messages</h2></div>} />
              <Route path="announcements" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Announcements</h2></div>} />
              <Route path="library" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">File Library</h2></div>} />
            </Route>

            {/* Auth Module */}
            <Route path="/auth-module">
              <Route path="authentication" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Authentication</h2></div>} />
              <Route path="requests" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Requests</h2></div>} />
              <Route path="authorization" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Authorization</h2></div>} />
              <Route path="contact" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Contact Form</h2></div>} />
            </Route>

            {/* Admin Module */}
            <Route path="/admin">
              <Route path="users" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">User Management</h2></div>} />
              <Route path="password-policy" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Password Policy</h2></div>} />
              <Route path="roles" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Roles & Permissions</h2></div>} />
              <Route path="entities" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Entities Database</h2></div>} />
              <Route path="entity-updater" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Entity Data Updater</h2></div>} />
            </Route>

            {/* Subject Management */}
            <Route path="/manage-subjects" element={<ManageSubjectsPage />} />
            <Route path="/subjects/:subjectId/manage" element={<SubjectManagementPage />} />

            {/* FAQ Page */}
            <Route path="/faq" element={<FAQPage />} />

            {/* 404 */}
            <Route path="*" element={<div className="p-6 bg-white rounded-lg shadow"><h2 className="text-2xl font-bold">Page Not Found</h2></div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

