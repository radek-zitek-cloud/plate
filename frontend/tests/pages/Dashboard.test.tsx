import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Dashboard from '../../src/pages/Dashboard';
import { mockUser, mockUserWithoutFullName, mockAdminUser } from '../utils/mockData';

const mockNavigate = vi.fn();
const mockLogout = vi.fn();

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../../src/context/AuthContext', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../context/AuthContext')>();
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  return <BrowserRouter>{children}</BrowserRouter>;
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders welcome message with full name', async () => {
      const { useAuth } = await import('../../src/context/AuthContext');
      vi.mocked(useAuth).mockReturnValue({
        user: mockUser,
        setUser: vi.fn(),
        loading: false,
        login: vi.fn(),
        signup: vi.fn(),
        logout: mockLogout,
      });

      render(<Dashboard />, { wrapper: TestWrapper });
      expect(screen.getByText(`Welcome, ${mockUser.full_name}!`)).toBeInTheDocument();
    });

    it('renders welcome message with username when no full name', async () => {
      const { useAuth } = await import('../../src/context/AuthContext');
      vi.mocked(useAuth).mockReturnValue({
        user: mockUserWithoutFullName,
        setUser: vi.fn(),
        loading: false,
        login: vi.fn(),
        signup: vi.fn(),
        logout: mockLogout,
      });

      render(<Dashboard />, { wrapper: TestWrapper });
      expect(
        screen.getByText(`Welcome, ${mockUserWithoutFullName.username}!`)
      ).toBeInTheDocument();
    });

    it('displays user information correctly', async () => {
      const { useAuth } = await import('../../src/context/AuthContext');
      vi.mocked(useAuth).mockReturnValue({
        user: mockUser,
        setUser: vi.fn(),
        loading: false,
        login: vi.fn(),
        signup: vi.fn(),
        logout: mockLogout,
      });

      render(<Dashboard />, { wrapper: TestWrapper });

      expect(screen.getByText(mockUser.full_name!)).toBeInTheDocument();
      expect(screen.getByText(mockUser.username)).toBeInTheDocument();
      expect(screen.getByText(mockUser.email)).toBeInTheDocument();
    });

    it('displays admin badge for superuser', async () => {
      const { useAuth } = await import('../../src/context/AuthContext');
      vi.mocked(useAuth).mockReturnValue({
        user: mockAdminUser,
        setUser: vi.fn(),
        loading: false,
        login: vi.fn(),
        signup: vi.fn(),
        logout: mockLogout,
      });

      render(<Dashboard />, { wrapper: TestWrapper });
      const adminBadge = screen.getByText((content, element) => {
        return element?.classList.contains('role-badge') && element?.classList.contains('admin');
      });
      expect(adminBadge).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('navigates to profile when profile button clicked', async () => {
      const { useAuth } = await import('../../src/context/AuthContext');
      vi.mocked(useAuth).mockReturnValue({
        user: mockUser,
        setUser: vi.fn(),
        loading: false,
        login: vi.fn(),
        signup: vi.fn(),
        logout: mockLogout,
      });

      const user = userEvent.setup();
      render(<Dashboard />, { wrapper: TestWrapper });

      const profileButton = screen.getByRole('button', { name: /profile settings/i });
      await user.click(profileButton);

      expect(mockNavigate).toHaveBeenCalledWith('/profile');
    });

    it('logs out and navigates to login', async () => {
      const { useAuth } = await import('../../src/context/AuthContext');
      vi.mocked(useAuth).mockReturnValue({
        user: mockUser,
        setUser: vi.fn(),
        loading: false,
        login: vi.fn(),
        signup: vi.fn(),
        logout: mockLogout,
      });

      const user = userEvent.setup();
      render(<Dashboard />, { wrapper: TestWrapper });

      const logoutButton = screen.getByRole('button', { name: /logout/i });
      await user.click(logoutButton);

      expect(mockLogout).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });
});
