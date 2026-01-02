import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../../src/context/AuthContext';
import * as authApi from '../../src/api/auth';
import { mockUser, mockLoginResponse } from '../utils/mockData';

// Mock the auth API
vi.mock('../../src/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    signup: vi.fn(),
    getMe: vi.fn(),
    testToken: vi.fn(),
  },
}));

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  describe('useAuth hook', () => {
    it('throws error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        renderHook(() => useAuth());
      }).toThrow('useAuth must be used within an AuthProvider');

      spy.mockRestore();
    });
  });

  describe('Initial authentication', () => {
    it('initializes with no user when no token in localStorage', async () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      }, { timeout: 2000 });

      expect(result.current.user).toBeNull();
      expect(authApi.authApi.testToken).not.toHaveBeenCalled();
    });

    it('loads user from token when token exists in localStorage', async () => {
      window.localStorage.setItem('token', 'existing-token');
      vi.mocked(authApi.authApi.testToken).mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      }, { timeout: 2000 });

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
      }, { timeout: 2000 });

      expect(authApi.authApi.testToken).toHaveBeenCalled();
    });

    it('removes invalid token and sets user to null', async () => {
      window.localStorage.setItem('token', 'invalid-token');
      vi.mocked(authApi.authApi.testToken).mockRejectedValue(new Error('Invalid token'));

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      }, { timeout: 2000 });

      expect(result.current.user).toBeNull();
      expect(window.localStorage.getItem('token')).toBeNull();
    });
  });

  describe('login', () => {
    it('logs in user successfully', async () => {
      vi.mocked(authApi.authApi.login).mockResolvedValue(mockLoginResponse);
      vi.mocked(authApi.authApi.getMe).mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      }, { timeout: 2000 });

      await result.current.login('test@example.com', 'password123');

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
      }, { timeout: 2000 });

      expect(authApi.authApi.login).toHaveBeenCalledWith({
        username: 'test@example.com',
        password: 'password123',
      });
      expect(window.localStorage.getItem('token')).toBe(mockLoginResponse.access_token);
    });

    it('throws error on failed login', async () => {
      vi.mocked(authApi.authApi.login).mockRejectedValue(
        new Error('Invalid credentials')
      );

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(
        result.current.login('test@example.com', 'wrongpassword')
      ).rejects.toThrow('Invalid credentials');

      expect(result.current.user).toBeNull();
    });
  });

  describe('signup', () => {
    it('signs up and logs in user successfully', async () => {
      vi.mocked(authApi.authApi.signup).mockResolvedValue(mockUser);
      vi.mocked(authApi.authApi.login).mockResolvedValue(mockLoginResponse);
      vi.mocked(authApi.authApi.getMe).mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      }, { timeout: 2000 });

      await result.current.signup(
        'test@example.com',
        'testuser',
        'password123',
        'Test User'
      );

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
      }, { timeout: 2000 });

      expect(authApi.authApi.signup).toHaveBeenCalledWith({
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123',
        full_name: 'Test User',
      });
      expect(authApi.authApi.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
    });
  });

  describe('logout', () => {
    it('logs out user and clears state', async () => {
      window.localStorage.setItem('token', 'existing-token');
      vi.mocked(authApi.authApi.testToken).mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
      }, { timeout: 2000 });

      result.current.logout();

      await waitFor(() => {
        expect(result.current.user).toBeNull();
      }, { timeout: 2000 });

      expect(window.localStorage.getItem('token')).toBeNull();
    });
  });

  describe('setUser', () => {
    it('allows updating user state directly', async () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      }, { timeout: 2000 });

      const updatedUser = { ...mockUser, full_name: 'Updated Name' };
      result.current.setUser(updatedUser);

      await waitFor(() => {
        expect(result.current.user).toEqual(updatedUser);
      }, { timeout: 2000 });
    });
  });
});
