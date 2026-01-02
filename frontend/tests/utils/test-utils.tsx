import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';

interface AllProvidersProps {
  children: React.ReactNode;
}

/**
 * Wrapper component that includes all necessary providers for testing
 */
const AllProviders = ({ children }: AllProvidersProps) => {
  return (
    <BrowserRouter>
      <AuthProvider>{children}</AuthProvider>
    </BrowserRouter>
  );
};

/**
 * Custom render function that wraps components with necessary providers
 * @param ui - Component to render
 * @param options - Render options
 */
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };
