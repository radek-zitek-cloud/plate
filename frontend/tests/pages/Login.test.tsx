import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Login from '../../src/pages/Login';

const mockNavigate = vi.fn();
const mockLogin = vi.fn();

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../../src/context/AuthContext', () => ({
  useAuth: () => ({
    login: mockLogin,
    user: null,
    loading: false,
    signup: vi.fn(),
    logout: vi.fn(),
    setUser: vi.fn(),
  }),
}));

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  return <BrowserRouter>{children}</BrowserRouter>;
};

describe('Login Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders login form with all fields', () => {
      render(<Login />, { wrapper: TestWrapper });

      expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/username or email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
      expect(screen.getByText(/don't have an account/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /sign up/i })).toBeInTheDocument();
    });

    it('renders with username field focused', () => {
      render(<Login />, { wrapper: TestWrapper });
      const usernameInput = screen.getByLabelText(/username or email/i);
      expect(usernameInput).toHaveFocus();
    });
  });

  describe('Form Interaction', () => {
    it('allows user to type in username field', async () => {
      const user = userEvent.setup();
      render(<Login />, { wrapper: TestWrapper });

      const usernameInput = screen.getByLabelText(/username or email/i);
      await user.clear(usernameInput);
      await user.type(usernameInput, 'testuser');

      expect(usernameInput).toHaveValue('testuser');
    });

    it('allows user to type in password field', async () => {
      const user = userEvent.setup();
      render(<Login />, { wrapper: TestWrapper });

      const passwordInput = screen.getByLabelText(/^password$/i);
      await user.type(passwordInput, 'password123');

      expect(passwordInput).toHaveValue('password123');
    });

    it('password field masks input', () => {
      render(<Login />, { wrapper: TestWrapper });
      const passwordInput = screen.getByLabelText(/^password$/i);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });
  });

  describe('Form Submission', () => {
    it('calls login function with correct credentials on submit', async () => {
      const user = userEvent.setup();
      mockLogin.mockResolvedValue(undefined);

      render(<Login />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/username or email/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.click(screen.getByRole('button', { name: /login/i }));

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('testuser', 'password123');
      });
    });

    it('navigates to dashboard on successful login', async () => {
      const user = userEvent.setup();
      mockLogin.mockResolvedValue(undefined);

      render(<Login />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/username or email/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.click(screen.getByRole('button', { name: /login/i }));

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('shows loading state during login', async () => {
      const user = userEvent.setup();
      let resolveLogin: () => void;
      const loginPromise = new Promise<void>((resolve) => {
        resolveLogin = resolve;
      });
      mockLogin.mockReturnValue(loginPromise);

      render(<Login />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/username or email/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.click(screen.getByRole('button', { name: /login/i }));

      const submitButton = screen.getByRole('button', { name: /logging in\.\.\./i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toBeDisabled();

      resolveLogin!();
    });

    it('disables form fields during login', async () => {
      const user = userEvent.setup();
      let resolveLogin: () => void;
      const loginPromise = new Promise<void>((resolve) => {
        resolveLogin = resolve;
      });
      mockLogin.mockReturnValue(loginPromise);

      render(<Login />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/username or email/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.click(screen.getByRole('button', { name: /login/i }));

      expect(screen.getByLabelText(/username or email/i)).toBeDisabled();
      expect(screen.getByLabelText(/^password$/i)).toBeDisabled();

      resolveLogin!();
    });
  });

  describe('Error Handling', () => {
    it('displays error message on login failure with detail', async () => {
      const user = userEvent.setup();
      mockLogin.mockRejectedValue({
        response: {
          data: {
            detail: 'Invalid credentials',
          },
        },
      });

      render(<Login />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/username or email/i), 'wronguser');
      await user.type(screen.getByLabelText(/^password$/i), 'wrongpass');
      await user.click(screen.getByRole('button', { name: /login/i }));

      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
    });

    it('displays generic error message when detail is missing', async () => {
      const user = userEvent.setup();
      mockLogin.mockRejectedValue(new Error('Network error'));

      render(<Login />, { wrapper: TestWrapper });

      await user.type(screen.getByLabelText(/username or email/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.click(screen.getByRole('button', { name: /login/i }));

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });

    it('clears error message on new submission', async () => {
      const user = userEvent.setup();
      mockLogin.mockRejectedValueOnce({
        response: { data: { detail: 'Invalid credentials' } },
      });

      render(<Login />, { wrapper: TestWrapper });

      // First failed attempt
      await user.type(screen.getByLabelText(/username or email/i), 'wronguser');
      await user.type(screen.getByLabelText(/^password$/i), 'wrongpass');
      await user.click(screen.getByRole('button', { name: /login/i }));

      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });

      // Second attempt - error should be cleared
      mockLogin.mockResolvedValue(undefined);
      await user.clear(screen.getByLabelText(/username or email/i));
      await user.clear(screen.getByLabelText(/^password$/i));
      await user.type(screen.getByLabelText(/username or email/i), 'testuser');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.click(screen.getByRole('button', { name: /login/i }));

      await waitFor(() => {
        expect(screen.queryByText('Invalid credentials')).not.toBeInTheDocument();
      });
    });
  });

  describe('Navigation', () => {
    it('has working link to signup page', () => {
      render(<Login />, { wrapper: TestWrapper });
      const signupLink = screen.getByRole('link', { name: /sign up/i });
      expect(signupLink).toHaveAttribute('href', '/signup');
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      render(<Login />, { wrapper: TestWrapper });
      expect(screen.getByLabelText(/username or email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    });

    it('requires username and password fields', () => {
      render(<Login />, { wrapper: TestWrapper });
      expect(screen.getByLabelText(/username or email/i)).toBeRequired();
      expect(screen.getByLabelText(/^password$/i)).toBeRequired();
    });
  });
});
