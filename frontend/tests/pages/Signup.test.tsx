import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Signup from '../../src/pages/Signup';

const mockNavigate = vi.fn();
const mockSignup = vi.fn();

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../../src/context/AuthContext', () => ({
  useAuth: () => ({
    signup: mockSignup,
    user: null,
    loading: false,
    login: vi.fn(),
    logout: vi.fn(),
    setUser: vi.fn(),
  }),
}));

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  return <BrowserRouter>{children}</BrowserRouter>;
};

describe('Signup Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders signup form with all fields', () => {
      render(<Signup />, { wrapper: TestWrapper });

      expect(screen.getByRole('heading', { name: /sign up/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^username$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
      expect(screen.getByText(/already have an account/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /login/i })).toBeInTheDocument();
    });

    it('renders with email field focused', () => {
      render(<Signup />, { wrapper: TestWrapper });
      const emailInput = screen.getByLabelText(/^email$/i);
      expect(emailInput).toHaveFocus();
    });

    it('marks full name as optional', () => {
      render(<Signup />, { wrapper: TestWrapper });
      expect(screen.getByLabelText(/full name \(optional\)/i)).toBeInTheDocument();
    });
  });

  describe('Form Interaction', () => {
    it('allows user to type in all fields', async () => {
      const user = userEvent.setup();
      render(<Signup />, { wrapper: TestWrapper });

      const emailInput = screen.getByLabelText(/^email$/i);
      const usernameInput = screen.getByLabelText(/^username$/i);
      const fullNameInput = screen.getByLabelText(/full name/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(fullNameInput, 'Test User');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');

      expect(emailInput).toHaveValue('test@example.com');
      expect(usernameInput).toHaveValue('testuser');
      expect(fullNameInput).toHaveValue('Test User');
      expect(passwordInput).toHaveValue('password123');
      expect(confirmPasswordInput).toHaveValue('password123');
    });

    it('password fields mask input', () => {
      render(<Signup />, { wrapper: TestWrapper });
      expect(screen.getByLabelText(/^password$/i)).toHaveAttribute('type', 'password');
      expect(screen.getByLabelText(/confirm password/i)).toHaveAttribute('type', 'password');
    });

    it('password fields have minLength of 8', () => {
      render(<Signup />, { wrapper: TestWrapper });
      expect(screen.getByLabelText(/^password$/i)).toHaveAttribute('minLength', '8');
      expect(screen.getByLabelText(/confirm password/i)).toHaveAttribute('minLength', '8');
    });
  });

  describe('Form Validation', () => {
    it('shows error when passwords do not match', async () => {
      const user = userEvent.setup();
      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'differentpassword');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      expect(await screen.findByText('Passwords do not match')).toBeInTheDocument();
      expect(mockSignup).not.toHaveBeenCalled();
    });

    it('shows error when password is too short', async () => {
      const user = userEvent.setup();
      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'short');
      await user.type(screen.getByLabelText(/confirm password/i), 'short');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      expect(await screen.findByText('Password must be at least 8 characters long')).toBeInTheDocument();
      expect(mockSignup).not.toHaveBeenCalled();
    });

    it('validates password length before matching', async () => {
      const user = userEvent.setup();
      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'short');
      await user.type(screen.getByLabelText(/confirm password/i), 'different');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      // Should check password mismatch first
      expect(await screen.findByText('Passwords do not match')).toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('calls signup function with correct data on submit', async () => {
      const user = userEvent.setup();
      mockSignup.mockResolvedValue(undefined);

      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/full name/i), 'Test User');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(mockSignup).toHaveBeenCalledWith(
          'test@example.com',
          'testuser',
          'password123',
          'Test User'
        );
      });
    });

    it('calls signup without full name if not provided', async () => {
      const user = userEvent.setup();
      mockSignup.mockResolvedValue(undefined);

      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(mockSignup).toHaveBeenCalledWith(
          'test@example.com',
          'testuser',
          'password123',
          undefined
        );
      });
    });

    it('navigates to dashboard on successful signup', async () => {
      const user = userEvent.setup();
      mockSignup.mockResolvedValue(undefined);

      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('shows loading state during signup', async () => {
      const user = userEvent.setup();
      let resolveSignup: () => void;
      const signupPromise = new Promise<void>((resolve) => {
        resolveSignup = resolve;
      });
      mockSignup.mockReturnValue(signupPromise);

      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      const submitButton = screen.getByRole('button', { name: /creating account\.\.\./i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toBeDisabled();

      resolveSignup!();
    });

    it('disables form fields during signup', async () => {
      const user = userEvent.setup();
      let resolveSignup: () => void;
      const signupPromise = new Promise<void>((resolve) => {
        resolveSignup = resolve;
      });
      mockSignup.mockReturnValue(signupPromise);

      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      expect(screen.getByLabelText(/^email$/i)).toBeDisabled();
      expect(screen.getByLabelText(/^username$/i)).toBeDisabled();
      expect(screen.getByLabelText(/full name/i)).toBeDisabled();
      expect(screen.getByLabelText(/^password$/i)).toBeDisabled();
      expect(screen.getByLabelText(/confirm password/i)).toBeDisabled();

      resolveSignup!();
    });
  });

  describe('Error Handling', () => {
    it('displays error message on signup failure with string detail', async () => {
      const user = userEvent.setup();
      mockSignup.mockRejectedValue({
        response: {
          data: {
            detail: 'Email already registered',
          },
        },
      });

      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'existing@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.getByText('Email already registered')).toBeInTheDocument();
      });
    });

    it('displays error messages from array detail', async () => {
      const user = userEvent.setup();
      mockSignup.mockRejectedValue({
        response: {
          data: {
            detail: [
              { msg: 'Email already exists' },
              { msg: 'Username already taken' },
            ],
          },
        },
      });

      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'existing@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'existinguser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.getByText('Email already exists, Username already taken')).toBeInTheDocument();
      });
    });

    it('displays generic error message when detail is missing', async () => {
      const user = userEvent.setup();
      mockSignup.mockRejectedValue(new Error('Network error'));

      render(<Signup />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });

    it('clears error message on new submission', async () => {
      const user = userEvent.setup();
      mockSignup.mockRejectedValueOnce({
        response: { data: { detail: 'Email already registered' } },
      });

      render(<Signup />, { wrapper: TestWrapper });

      // First failed attempt
      await user.type(screen.getByLabelText(/^email$/i), 'existing@example.com');
      await user.type(screen.getByLabelText(/^username$/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.getByText('Email already registered')).toBeInTheDocument();
      });

      // Second attempt - error should be cleared
      mockSignup.mockResolvedValue(undefined);
      await user.clear(screen.getByLabelText(/^email$/i));
      await user.type(screen.getByLabelText(/^email$/i), 'new@example.com');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.queryByText('Email already registered')).not.toBeInTheDocument();
      });
    });
  });

  describe('Navigation', () => {
    it('has working link to login page', () => {
      render(<Signup />, { wrapper: TestWrapper });
      const loginLink = screen.getByRole('link', { name: /login/i });
      expect(loginLink).toHaveAttribute('href', '/login');
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      render(<Signup />, { wrapper: TestWrapper });
      expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^username$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    });

    it('requires email, username, and password fields', () => {
      render(<Signup />, { wrapper: TestWrapper });
      expect(screen.getByLabelText(/^email$/i)).toBeRequired();
      expect(screen.getByLabelText(/^username$/i)).toBeRequired();
      expect(screen.getByLabelText(/^password$/i)).toBeRequired();
      expect(screen.getByLabelText(/confirm password/i)).toBeRequired();
    });

    it('does not require full name field', () => {
      render(<Signup />, { wrapper: TestWrapper });
      expect(screen.getByLabelText(/full name/i)).not.toBeRequired();
    });

    it('has correct email input type', () => {
      render(<Signup />, { wrapper: TestWrapper });
      expect(screen.getByLabelText(/^email$/i)).toHaveAttribute('type', 'email');
    });
  });
});
