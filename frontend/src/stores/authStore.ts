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

      login: async (email: string, password: string) => {
        try {
          const response = await authAPI.login(email, password);
          
          // Store session ID
          localStorage.setItem('sessionId', response.session_id);
          
          // TODO: Fetch user details and determine role
          // For now, mock the user
          const mockUser: User = {
            ID: 1,
            USER_NAME: 'Demo',
            USER_LASTNAME: 'User',
            EMAIL: email,
            PHONE: null,
            IS_USER_ACTIVE: true,
          };
          
          const role: UserRole = email.includes('admin') ? 'administrator' : 'internal_user';
          
          set({
            user: mockUser,
            sessionId: response.session_id,
            role,
            isAuthenticated: true,
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
      }),
    }
  )
);

