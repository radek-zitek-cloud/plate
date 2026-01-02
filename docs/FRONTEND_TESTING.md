# Frontend Testing Architecture

This document describes the testing setup and best practices for the frontend application.

## Testing Stack

- **Test Runner**: [Vitest](https://vitest.dev/) - Fast, Vite-native test runner
- **Testing Library**: [@testing-library/react](https://testing-library.com/react) - React component testing utilities
- **User Interactions**: [@testing-library/user-event](https://testing-library.com/docs/user-event/intro) - Simulates real user interactions
- **DOM Matchers**: [@testing-library/jest-dom](https://github.com/testing-library/jest-dom) - Custom Jest matchers for DOM assertions
- **Environment**: [jsdom](https://github.com/jsdom/jsdom) - Browser-like environment for tests

## Running Tests

```bash
# Run all tests once
npm test

# Run tests in watch mode (interactive)
npm run test:watch

# Run tests with UI
npm run test:ui

# Run tests with coverage report
npm run test:coverage
```

## Test File Structure

```
frontend/src/
├── test/
│   ├── setup.ts           # Global test setup
│   ├── test-utils.tsx     # Custom render with providers
│   └── mockData.ts        # Shared mock data
├── pages/
│   ├── Profile.tsx
│   ├── Profile.test.tsx   # Component tests
│   ├── Dashboard.tsx
│   └── Dashboard.test.tsx
└── context/
    ├── AuthContext.tsx
    └── AuthContext.test.tsx
```

## Testing Guidelines

### 1. Test File Naming

- Place test files next to the component they test
- Name test files with `.test.tsx` or `.test.ts` suffix
- Example: `Profile.tsx` → `Profile.test.tsx`

### 2. What to Test

✅ **DO Test:**
- User interactions (clicks, typing, form submissions)
- Conditional rendering based on props/state
- Error states and error messages
- Success states and success messages
- Form validation
- API calls and responses (mocked)
- Navigation behavior

❌ **DON'T Test:**
- Implementation details (internal state)
- Third-party library behavior
- Styling (unless it affects functionality)
- Exact DOM structure

### 3. Test Structure

Use the **Arrange-Act-Assert** pattern:

```typescript
it('updates profile successfully', async () => {
  // Arrange
  const user = userEvent.setup();
  vi.mocked(authApi.updateProfile).mockResolvedValue(updatedUser);
  render(<Profile />);

  // Act
  await user.type(screen.getByLabelText(/full name/i), 'New Name');
  await user.click(screen.getByRole('button', { name: /update/i }));

  // Assert
  await waitFor(() => {
    expect(screen.getByText(/updated successfully/i)).toBeInTheDocument();
  });
});
```

### 4. Querying Elements

Priority order (from Testing Library best practices):

1. **Accessible by everyone**: `getByRole`, `getByLabelText`, `getByText`
2. **Semantic queries**: `getByAltText`, `getByTitle`
3. **Test IDs**: `getByTestId` (last resort)

```typescript
// ✅ Good - Uses accessible queries
screen.getByRole('button', { name: /submit/i });
screen.getByLabelText(/email/i);
screen.getByText(/welcome/i);

// ❌ Avoid - Relies on implementation details
screen.getByClassName('submit-button');
wrapper.find('.email-input');
```

### 5. Async Testing

Always use `waitFor` for async operations:

```typescript
await waitFor(() => {
  expect(screen.getByText(/success/i)).toBeInTheDocument();
});
```

### 6. Mocking

#### API Mocking

```typescript
// Mock API module
vi.mock('../api/auth', () => ({
  updateProfile: vi.fn(),
  changePassword: vi.fn(),
}));

// Set return value for specific test
vi.mocked(authApi.updateProfile).mockResolvedValue(mockUser);

// Simulate API error
vi.mocked(authApi.updateProfile).mockRejectedValue({
  response: { data: { detail: 'Error message' } },
});
```

#### Context Mocking

```typescript
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: mockUser,
    setUser: vi.fn(),
    loading: false,
    login: vi.fn(),
    signup: vi.fn(),
    logout: vi.fn(),
  }),
}));
```

### 7. User Events

Always use `userEvent` instead of `fireEvent`:

```typescript
const user = userEvent.setup();

// Type into input
await user.type(screen.getByLabelText(/email/i), 'test@example.com');

// Click button
await user.click(screen.getByRole('button', { name: /submit/i }));

// Clear input
await user.clear(screen.getByLabelText(/email/i));
```

### 8. Custom Render

Use the custom render from `test-utils.tsx` which includes all providers:

```typescript
import { render, screen } from '../test/test-utils';

render(<MyComponent />); // Automatically wrapped with Router and AuthProvider
```

## Coverage Goals

- **Statements**: > 80%
- **Branches**: > 80%
- **Functions**: > 80%
- **Lines**: > 80%

Focus on testing critical user paths and business logic rather than achieving 100% coverage.

## Common Patterns

### Testing Forms

```typescript
it('submits form with valid data', async () => {
  const user = userEvent.setup();
  const mockSubmit = vi.fn();

  render(<MyForm onSubmit={mockSubmit} />);

  await user.type(screen.getByLabelText(/name/i), 'John Doe');
  await user.type(screen.getByLabelText(/email/i), 'john@example.com');
  await user.click(screen.getByRole('button', { name: /submit/i }));

  await waitFor(() => {
    expect(mockSubmit).toHaveBeenCalledWith({
      name: 'John Doe',
      email: 'john@example.com',
    });
  });
});
```

### Testing Error States

```typescript
it('displays error message on failure', async () => {
  const user = userEvent.setup();
  vi.mocked(api.submit).mockRejectedValue({
    response: { data: { detail: 'Validation error' } },
  });

  render(<MyComponent />);

  await user.click(screen.getByRole('button', { name: /submit/i }));

  await waitFor(() => {
    expect(screen.getByText(/validation error/i)).toBeInTheDocument();
  });
});
```

### Testing Navigation

```typescript
const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => ({
  ...await vi.importActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

it('navigates to profile page', async () => {
  const user = userEvent.setup();
  render(<MyComponent />);

  await user.click(screen.getByRole('button', { name: /profile/i }));

  expect(mockNavigate).toHaveBeenCalledWith('/profile');
});
```

## Debugging Tests

```typescript
// Print DOM tree
screen.debug();

// Print specific element
screen.debug(screen.getByRole('button'));

// Check what's queryable
screen.logTestingPlaygroundURL();
```

## CI/CD Integration

Tests run automatically in CI/CD pipeline. The build will fail if:
- Any test fails
- Coverage thresholds are not met

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [User Event Documentation](https://testing-library.com/docs/user-event/intro)
