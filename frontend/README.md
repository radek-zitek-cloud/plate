# Frontend

React TypeScript application built with Vite, providing authentication UI for the backend API.

## Features

- **Authentication**: Login, Signup, and Logout functionality
- **Protected Routes**: Dashboard accessible only to authenticated users
- **Token Management**: JWT token storage in localStorage
- **Modern Stack**: React 18, TypeScript, React Router, Axios
- **Hot Module Replacement**: Fast refresh during development

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client and auth endpoints
│   ├── components/    # Reusable components (ProtectedRoute)
│   ├── context/       # React Context (AuthContext)
│   ├── pages/         # Page components (Login, Signup, Dashboard)
│   ├── App.tsx        # Main app with routing
│   └── main.tsx       # Entry point
├── public/            # Static assets
├── Dockerfile         # Production build
├── Dockerfile.dev     # Development container
└── nginx.conf         # Nginx config for production
```

## Development

The frontend runs in a Docker container with hot reload enabled:

```bash
# Start development environment
make dev

# Frontend will be available at http://localhost:5173
```

### Environment Variables

- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)

Configuration files:
- `.env.development` - Development environment
- `.env.production` - Production build

## API Integration

The frontend communicates with the backend API at `/api/v1`:

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/test-token` - Validate token
- `POST /api/v1/users/signup` - User registration
- `GET /api/v1/users/me` - Get current user

### Authentication Flow

1. User logs in or signs up
2. JWT token received and stored in localStorage
3. Token automatically added to all subsequent API requests
4. Protected routes check for valid token before rendering
5. Logout removes token from localStorage

## Pages

### Login (`/login`)
- Username/email and password fields
- Redirects to dashboard on success
- Link to signup page

### Signup (`/signup`)
- Email, username, password, and confirm password fields
- Optional full name field
- Auto-login after successful registration
- Link to login page

### Dashboard (`/dashboard`)
- Protected route (requires authentication)
- Displays user information
- Logout button

## Components

### AuthProvider
React Context provider that:
- Manages authentication state
- Handles login/signup/logout
- Validates token on app load
- Provides auth methods to child components

### ProtectedRoute
HOC that:
- Checks if user is authenticated
- Shows loading state while validating
- Redirects to login if not authenticated
- Renders protected content if authenticated

## Building for Production

```bash
# Build production image
docker compose -f docker-compose.prod.yml build frontend

# Production build uses Nginx to serve static files
```

The production Dockerfile:
1. Builds the React app with Vite
2. Serves static files with Nginx
3. Configures SPA routing
4. Adds security headers
5. Enables gzip compression

## Development Commands

```bash
# Install dependencies locally
cd frontend
npm install

# Run dev server locally (outside Docker)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Styling

CSS is organized by component:
- `pages/Auth.css` - Login and Signup styling
- `pages/Dashboard.css` - Dashboard styling
- `App.css` - Global styles

Design features:
- Modern gradient backgrounds
- Clean card-based layouts
- Smooth transitions and hover effects
- Responsive design
- Form validation styling

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES2015+ support required
- No IE11 support

