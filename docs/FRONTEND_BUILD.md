# Frontend Build Configuration

## Overview

The frontend is a React + Vite application that requires build-time configuration for production deployments. This document explains how environment variables are handled during the build process.

## Environment Variables

### VITE_API_URL

**Purpose**: Tells the frontend where to find the backend API

**Type**: Build-time environment variable (baked into compiled JavaScript)

**Default**: `http://localhost:8000`

**Usage in Code**:
```typescript
// src/api/auth.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### How It Works

1. **Development**: Uses `.env.development` file
2. **Production Build**: Needs to be provided as build argument
3. **Vite Processing**: Reads from `import.meta.env.VITE_API_URL`
4. **Build Output**: Value is compiled into JavaScript (can't be changed at runtime)

## Build Configurations

### Local Development

```bash
cd frontend
npm run dev
```

Uses `frontend/.env.development`:
```
VITE_API_URL=http://localhost:8000
```

### Docker Development

```bash
docker compose up
```

Uses `Dockerfile.dev` with default value or override:
```bash
VERSION=0.1.0 docker compose build frontend
```

### Docker Production

```bash
# Build with custom API URL
docker build \
  --build-arg VITE_API_URL=https://api.yourdomain.com \
  -f frontend/Dockerfile \
  frontend/
```

### Railway Deployment

**Critical Steps**:

1. Go to Railway Dashboard → Frontend Service
2. Navigate to: **Settings → Build → Build Arguments**
3. Add build argument:
   ```
   VITE_API_URL=https://your-backend.up.railway.app
   ```
4. Get the backend URL from Backend Service → Settings → Networking → Public Domain
5. Trigger rebuild (Settings → Redeploy or push new commit)

**Common Mistake**: Setting `VITE_API_URL` as a runtime environment variable won't work! It must be a **build argument**.

## Dockerfile Structure

```dockerfile
# Build stage
FROM node:24-alpine AS builder

# Accept build arguments
ARG VERSION=0.0.0
ARG VITE_API_URL=http://localhost:8000

# Set as environment variables for Vite to read
ENV VERSION=${VERSION}
ENV VITE_API_URL=${VITE_API_URL}

# Install dependencies and build
RUN npm ci
COPY . .
RUN npm run build  # Vite bakes env vars into build here

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

## Verification

### Check Build Output

After building, verify the API URL in the compiled JavaScript:

```bash
# Build the image
docker build --build-arg VITE_API_URL=https://api.example.com -t frontend frontend/

# Run and check
docker run --rm frontend cat /usr/share/nginx/html/assets/*.js | grep -o 'https://api.example.com'
```

### Check Runtime

1. Open browser developer tools
2. Go to Network tab
3. Trigger an API call (e.g., login)
4. Verify request goes to correct URL:
   - ✅ Should be: `https://your-backend.up.railway.app/api/v1/...`
   - ❌ Should NOT be: `http://localhost:8000/api/v1/...`

## Troubleshooting

### Frontend tries to connect to localhost:8000

**Symptom**: Console error `ERR_CONNECTION_REFUSED` to `localhost:8000`

**Cause**: `VITE_API_URL` not set as build argument

**Fix**:
1. Ensure `VITE_API_URL` is in Railway build arguments (not runtime variables)
2. Rebuild the frontend service
3. Verify the URL is correct

### Changes to VITE_API_URL don't take effect

**Cause**: Changed runtime variable instead of build argument, or didn't rebuild

**Fix**:
1. Set as **build argument** in Railway
2. Trigger a rebuild (push commit or manual redeploy)
3. Wait for build to complete
4. Hard refresh browser (Ctrl+Shift+R)

### .env.production file overrides build argument

**Cause**: `.env.production` file not excluded by `.dockerignore`

**Fix**:
1. Verify `frontend/.dockerignore` contains `.env.*`
2. The Dockerfile ENV vars take precedence over `.env.production`
3. If issues persist, temporarily remove `.env.production`

## Build Scripts

### Using scripts/build-images.sh

```bash
# Build with custom API URL
./scripts/build-images.sh --api-url https://api.yourdomain.com

# Build and push to registry
./scripts/build-images.sh --push --registry ghcr.io/yourorg --api-url https://api.yourdomain.com
```

### Using docker-compose

```bash
# Production build with environment variable
VITE_API_URL=https://api.yourdomain.com docker compose -f docker-compose.prod.yaml build frontend

# Or export for multiple commands
export VITE_API_URL=https://api.yourdomain.com
docker compose -f docker-compose.prod.yaml build
docker compose -f docker-compose.prod.yaml up -d
```

## Best Practices

1. **Never hardcode API URLs** in source code - always use environment variables
2. **Set VITE_API_URL for production** - don't rely on defaults
3. **Use HTTPS in production** - Railway provides SSL automatically
4. **Verify after deployment** - Check browser console for correct API URL
5. **Document your backend URL** - Keep track of Railway domain or custom domain
6. **Rebuild after URL changes** - Build-time variables require rebuild

## References

- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Railway Build Arguments](https://docs.railway.app/deploy/builds)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
