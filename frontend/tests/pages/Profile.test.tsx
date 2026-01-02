import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { Profile } from '../../src/pages/Profile';
import * as authApi from '../../src/api/auth';
import { mockUser } from '../utils/mockData';

// Mock the API functions
vi.mock('../../src/api/auth', async (importOriginal) => {
  const actual = await importOriginal<typeof authApi>();
  return {
    ...actual,
    updateProfile: vi.fn(),
    changePassword: vi.fn(),
  };
});

// Mock the AuthContext
const mockSetUser = vi.fn();
const mockLogout = vi.fn();
const mockLogin = vi.fn();
const mockSignup = vi.fn();

vi.mock('../../src/context/AuthContext', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../context/AuthContext')>();
  return {
    ...actual,
    useAuth: () => ({
      user: mockUser,
      setUser: mockSetUser,
      loading: false,
      login: mockLogin,
      signup: mockSignup,
      logout: mockLogout,
    }),
  };
});

// Wrapper component for tests
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  return <BrowserRouter>{children}</BrowserRouter>;
};

describe('Profile Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Profile Information Form', () => {
    it('renders profile form with user data', () => {
      render(<Profile />, { wrapper: TestWrapper });

      expect(screen.getByLabelText(/email/i)).toHaveValue(mockUser.email);
      expect(screen.getByLabelText(/username/i)).toHaveValue(mockUser.username);
      expect(screen.getByLabelText(/full name/i)).toHaveValue(mockUser.full_name);
    });

    it('updates profile successfully', async () => {
      const user = userEvent.setup();
      const updatedUser = { ...mockUser, full_name: 'Updated Name' };
      vi.mocked(authApi.updateProfile).mockResolvedValue(updatedUser);

      render(<Profile />, { wrapper: TestWrapper });

      const fullNameInput = screen.getByLabelText(/full name/i);
      await user.clear(fullNameInput);
      await user.type(fullNameInput, 'Updated Name');

      const submitButton = screen.getByRole('button', { name: /update profile/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/profile updated successfully/i)).toBeInTheDocument();
      });

      expect(authApi.updateProfile).toHaveBeenCalledWith({
        email: mockUser.email,
        username: mockUser.username,
        full_name: 'Updated Name',
      });
    });

    it('displays error when profile update fails', async () => {
      const user = userEvent.setup();
      const errorMessage = 'A user with this email already exists';
      vi.mocked(authApi.updateProfile).mockRejectedValue({
        response: { data: { detail: errorMessage } },
      });

      render(<Profile />, { wrapper: TestWrapper });

      const emailInput = screen.getByLabelText(/email/i);
      await user.clear(emailInput);
      await user.type(emailInput, 'taken@example.com');

      const submitButton = screen.getByRole('button', { name: /update profile/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('shows loading state during update', async () => {
      const user = userEvent.setup();
      vi.mocked(authApi.updateProfile).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockUser), 100))
      );

      render(<Profile />, { wrapper: TestWrapper });

      const submitButton = screen.getByRole('button', { name: /update profile/i });
      await user.click(submitButton);

      expect(screen.getByRole('button', { name: /saving.../i })).toBeDisabled();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /update profile/i })).toBeEnabled();
      });
    });
  });

  describe('Password Change Form', () => {
    it('renders password change form', () => {
      render(<Profile />, { wrapper: TestWrapper });

      expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^new password$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm new password/i)).toBeInTheDocument();
    });

    it('changes password successfully', async () => {
      const user = userEvent.setup();
      vi.mocked(authApi.changePassword).mockResolvedValue({
        message: 'Password updated successfully',
      });

      render(<Profile />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/current password/i), 'oldpassword');
      await user.type(screen.getByLabelText(/^new password$/i), 'newpassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'newpassword123');

      const submitButton = screen.getByRole('button', { name: /change password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password changed successfully/i)).toBeInTheDocument();
      });

      expect(authApi.changePassword).toHaveBeenCalledWith({
        current_password: 'oldpassword',
        new_password: 'newpassword123',
      });
    });

    it('validates passwords match', async () => {
      const user = userEvent.setup();

      render(<Profile />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/current password/i), 'oldpassword');
      await user.type(screen.getByLabelText(/^new password$/i), 'newpassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'differentpassword');

      const submitButton = screen.getByRole('button', { name: /change password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/new passwords do not match/i)).toBeInTheDocument();
      });

      expect(authApi.changePassword).not.toHaveBeenCalled();
    });

    it('validates password length', async () => {
      const user = userEvent.setup();

      render(<Profile />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/current password/i), 'oldpass');
      await user.type(screen.getByLabelText(/^new password$/i), 'short');
      await user.type(screen.getByLabelText(/confirm new password/i), 'short');

      const submitButton = screen.getByRole('button', { name: /change password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText(/password must be at least 8 characters long/i)
        ).toBeInTheDocument();
      });

      expect(authApi.changePassword).not.toHaveBeenCalled();
    });

    it('displays error when password change fails', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Incorrect current password';
      vi.mocked(authApi.changePassword).mockRejectedValue({
        response: { data: { detail: errorMessage } },
      });

      render(<Profile />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/current password/i), 'wrongpassword');
      await user.type(screen.getByLabelText(/^new password$/i), 'newpassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'newpassword123');

      const submitButton = screen.getByRole('button', { name: /change password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('clears password form after successful change', async () => {
      const user = userEvent.setup();
      vi.mocked(authApi.changePassword).mockResolvedValue({
        message: 'Password updated successfully',
      });

      render(<Profile />, { wrapper: TestWrapper });

      const currentPasswordInput = screen.getByLabelText(/current password/i);
      const newPasswordInput = screen.getByLabelText(/^new password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);

      await user.type(currentPasswordInput, 'oldpassword');
      await user.type(newPasswordInput, 'newpassword123');
      await user.type(confirmPasswordInput, 'newpassword123');

      const submitButton = screen.getByRole('button', { name: /change password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(currentPasswordInput).toHaveValue('');
        expect(newPasswordInput).toHaveValue('');
        expect(confirmPasswordInput).toHaveValue('');
      });
    });
  });

  describe('Form Interactions', () => {
    it('clears error message when submitting another form', async () => {
      const user = userEvent.setup();
      vi.mocked(authApi.updateProfile).mockRejectedValue({
        response: { data: { detail: 'Profile error' } },
      });

      render(<Profile />, { wrapper: TestWrapper });

      // Trigger profile error
      const profileSubmit = screen.getByRole('button', { name: /update profile/i });
      await user.click(profileSubmit);

      await waitFor(() => {
        expect(screen.getByText(/profile error/i)).toBeInTheDocument();
      });

      // Submit password form should clear the error
      vi.mocked(authApi.changePassword).mockResolvedValue({
        message: 'Password updated successfully',
      });

      await user.type(screen.getByLabelText(/current password/i), 'oldpass123');
      await user.type(screen.getByLabelText(/^new password$/i), 'newpass123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'newpass123');

      const passwordSubmit = screen.getByRole('button', { name: /change password/i });
      await user.click(passwordSubmit);

      await waitFor(() => {
        expect(screen.queryByText(/profile error/i)).not.toBeInTheDocument();
      });
    });
  });
});
