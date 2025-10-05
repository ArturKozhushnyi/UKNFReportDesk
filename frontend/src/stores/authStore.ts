/**
 * Authentication State Management
 * Uses Zustand for global state
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, UserRole } from '../types';
import { authAPI } from '../services/api';

interface AuthState {
  user: User | null;
  sessionId: string | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  firstName: string | null;
  lastName: string | null;
  subjectName: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User, sessionId: string, role: UserRole) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      sessionId: null,
      role: null,
      isAuthenticated: false,
      firstName: null,
      lastName: null,
      subjectName: null,

      login: async (email: string, password: string) => {
        try {
          const response = await authAPI.login(email, password);
          
          // Store session ID
          localStorage.setItem('sessionId', response.session_id);
          
          // Fetch user details from /me endpoint
          const userDetails = await authAPI.getMe(response.session_id);
          
          // Build user object
          const user: User = {
            ID: userDetails.user_id,
            USER_NAME: userDetails.firstName || '',
            USER_LASTNAME: userDetails.lastName || '',
            EMAIL: userDetails.email,
            PHONE: userDetails.phone,
            IS_USER_ACTIVE: userDetails.isActive,
          };
          
          // Determine role (can be enhanced with actual role from backend)
          const role: UserRole = email.includes('admin') ? 'administrator' : 'external_user';
          
          set({
            user,
            sessionId: response.session_id,
            role,
            isAuthenticated: true,
            firstName: userDetails.firstName,
            lastName: userDetails.lastName,
            subjectName: userDetails.subjectName,
          });
        } catch (error) {
          console.error('Login failed:', error);
          throw error;
        }
      },

      logout: async () => {
        const { sessionId } = get();
        if (sessionId) {
          try {
            await authAPI.logout(sessionId);
          } catch (error) {
            console.error('Logout failed:', error);
          }
        }
        
        localStorage.removeItem('sessionId');
        set({
          user: null,
          sessionId: null,
          role: null,
          isAuthenticated: false,
          firstName: null,
          lastName: null,
          subjectName: null,
        });
      },

      setUser: (user: User, sessionId: string, role: UserRole) => {
        set({
          user,
          sessionId,
          role,
          isAuthenticated: true,
        });
      },

      clearAuth: () => {
        localStorage.removeItem('sessionId');
        set({
          user: null,
          sessionId: null,
          role: null,
          isAuthenticated: false,
          firstName: null,
          lastName: null,
          subjectName: null,
        });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        sessionId: state.sessionId,
        role: state.role,
        isAuthenticated: state.isAuthenticated,
        firstName: state.firstName,
        lastName: state.lastName,
        subjectName: state.subjectName,
      }),
    }
  )
);

