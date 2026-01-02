import { type User } from '../api/auth';

/**
 * Mock user data for testing
 */
export const mockUser: User = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  full_name: 'Test User',
  is_active: true,
  is_superuser: false,
};

/**
 * Mock user without full name
 */
export const mockUserWithoutFullName: User = {
  id: 2,
  email: 'test2@example.com',
  username: 'testuser2',
  is_active: true,
  is_superuser: false,
};

/**
 * Mock admin user
 */
export const mockAdminUser: User = {
  id: 3,
  email: 'admin@example.com',
  username: 'admin',
  full_name: 'Admin User',
  is_active: true,
  is_superuser: true,
};

/**
 * Mock login response
 */
export const mockLoginResponse = {
  access_token: 'mock-jwt-token-12345',
  token_type: 'bearer',
};

/**
 * Mock error response from API
 */
export const mockErrorResponse = {
  response: {
    data: {
      detail: 'Invalid credentials',
    },
    status: 401,
  },
};
