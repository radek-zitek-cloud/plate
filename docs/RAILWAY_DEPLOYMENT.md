# Railway Deployment Guide

This guide walks you through deploying the application to [Railway.app](https://railway.app), a platform-as-a-service that provides managed infrastructure for modern applications.

## Prerequisites

- Railway account (free tier available at [railway.app](https://railway.app))
- Railway CLI (optional but recommended): `npm install -g @railway/cli`
- Git repository pushed to GitHub, GitLab, or Bitbucket
- Project tested locally with `make test`

## Architecture Overview

The application will be deployed as multiple Railway services:
- **Backend Service**: FastAPI application (from `backend/Dockerfile`)
- **Frontend Service**: Nginx serving React build (from `frontend/Dockerfile`)
- **PostgreSQL Database**: Railway's managed PostgreSQL
- **Redis**: Railway's managed Redis

Railway automatically handles:
- SSL/TLS certificates
- Load balancing
- Health checks
- Zero-downtime deployments
- Automatic rollbacks on failure

## Deployment Steps

### 1. Create Railway Project

1. Log in to [Railway dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select your repository
6. Railway will detect the Dockerfiles automatically

### 2. Set Up PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Railway creates a PostgreSQL instance and provides a `DATABASE_URL`
4. **Note**: The `DATABASE_URL` is automatically injected as an environment variable

**Important**: Railway provides `DATABASE_URL` in the format `postgres://...` or `postgresql://...`, but the application automatically converts it to `postgresql+asyncpg://...` for async SQLAlchemy support. You don't need to modify the URL manually - the conversion happens automatically via the `async_database_url` property in `backend/app/core/config.py`.

### 3. Set Up Redis

1. In your Railway project, click "+ New"
2. Select "Database" → "Add Redis"
3. Railway creates a Redis instance and provides a `REDIS_URL`
4. **Note**: The `REDIS_URL` is automatically injected as an environment variable

### 4. Configure Backend Service

1. Railway should auto-detect `backend/Dockerfile`
2. If not, manually create a service:
   - Click "+ New" → "Empty Service"
   - Go to Settings → Set Root Directory to `backend`
   - Set Dockerfile Path to `Dockerfile`

3. **Configure Environment Variables**:

   Go to the backend service → Variables tab and add:

   ```bash
   # Required Variables
   SECRET_KEY=<generate with: openssl rand -hex 32>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # CORS - Set to your frontend domain
   CORS_ORIGINS=https://your-frontend.up.railway.app,https://yourdomain.com

   # Optional: Override defaults
   WORKERS=2
   SQL_ECHO=False
   TESTING=False
   ```

   **Important**: `DATABASE_URL` and `REDIS_URL` are automatically set by Railway when you add those services.

4. **Configure Build Command** (Settings → Deploy):
   - Build Command: (auto-detected from Dockerfile)
   - Start Command: (auto-detected from Dockerfile CMD)

5. **Configure Health Check** (Settings → Deploy → Health Check):
   - Path: `/health`
   - Timeout: 10 seconds
   - Interval: 30 seconds

6. **Set Up Database Migrations**:

   In Settings → Deploy → Custom Start Command, change to run migrations first:
   ```bash
   sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers ${WORKERS:-2}"
   ```

   Or use Railway's Deploy Lifecycle (if available):
   - Release Command: `alembic upgrade head`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers ${WORKERS:-2}`

### 5. Configure Frontend Service

1. Railway should auto-detect `frontend/Dockerfile`
2. If not, manually create a service:
   - Click "+ New" → "Empty Service"
   - Go to Settings → Set Root Directory to `frontend`
   - Set Dockerfile Path to `Dockerfile`

3. **Configure Environment Variables** (Build-time):

   Go to the frontend service → Variables tab and add:

   ```bash
   # Backend API URL - use your backend service's Railway URL
   VITE_API_URL=https://your-backend.up.railway.app
   ```

   **Important**: Get the backend URL from the backend service's Settings → Networking → Public Domain.

4. **Configure Build**:
   - The Dockerfile handles the build automatically
   - Build args can be set in Variables if needed

5. **Configure Port**:
   - Frontend serves on port 80 (nginx default)
   - Railway will automatically handle this

### 6. Connect Services

Railway automatically creates private networking between services in the same project. The services can reference each other by:
- Service name (e.g., `postgres`, `redis`)
- Environment variables (`DATABASE_URL`, `REDIS_URL`)

### 7. Configure Custom Domains (Optional)

1. Go to each service → Settings → Networking
2. Click "Generate Domain" for a Railway subdomain (e.g., `your-app.up.railway.app`)
3. Or add a Custom Domain:
   - Click "Custom Domain"
   - Enter your domain (e.g., `api.yourdomain.com` for backend)
   - Add the CNAME record to your DNS provider
   - Railway automatically provisions SSL certificate

**Recommended setup**:
- Backend: `api.yourdomain.com` or `backend-yourapp.up.railway.app`
- Frontend: `yourdomain.com` or `frontend-yourapp.up.railway.app`

### 8. Deploy!

1. Railway automatically deploys when you push to your main branch
2. Monitor deployment in the Railway dashboard
3. Check logs for any errors
4. Verify health checks pass

## Environment Variables Reference

### Backend Service

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Auto-set | - | PostgreSQL connection (from Railway) |
| `REDIS_URL` | Auto-set | - | Redis connection (from Railway) |
| `SECRET_KEY` | **Yes** | - | JWT signing key (generate with `openssl rand -hex 32`) |
| `ALGORITHM` | No | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | 30 | Token expiration time |
| `CORS_ORIGINS` | **Yes** | - | Comma-separated allowed origins |
| `PORT` | Auto-set | 8000 | Railway sets this automatically |
| `WORKERS` | No | 4 | Number of Uvicorn workers |
| `SQL_ECHO` | No | False | Log SQL queries (debug only) |
| `TESTING` | No | False | Disable rate limiting for tests |

### Frontend Service

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | **Yes** | - | Backend API URL (build-time variable) |

## Post-Deployment Checklist

After deployment, verify:

- [ ] Backend health check passes: `https://your-backend.up.railway.app/health`
- [ ] API docs accessible: `https://your-backend.up.railway.app/api/v1/docs`
- [ ] Frontend loads: `https://your-frontend.up.railway.app`
- [ ] Can create an account (signup works)
- [ ] Can log in (authentication works)
- [ ] Can access dashboard (protected routes work)
- [ ] Database migrations applied successfully (check logs)
- [ ] CORS headers configured correctly (check browser console)
- [ ] Environment variables set correctly
- [ ] Health checks passing in Railway dashboard
- [ ] Custom domains configured (if applicable)
- [ ] SSL certificates active (Railway handles this)

## Continuous Deployment

Railway automatically deploys when you push to your connected branch (usually `main`):

1. Make changes locally
2. Test with `make test`
3. Commit and push to GitHub
4. Railway detects the push
5. Railway builds new Docker images
6. Railway runs health checks
7. Railway performs rolling deployment
8. Old version stays running until new version is healthy
9. Traffic switches to new version
10. Old version is terminated

**Zero-downtime deployments** are automatic!

## Rollback

If a deployment fails:

1. Railway automatically rolls back to the previous version
2. Or manually rollback in Railway dashboard:
   - Go to Deployments tab
   - Find the last successful deployment
   - Click "Redeploy"

## Monitoring and Logs

### View Logs

**Via Dashboard**:
1. Go to your service in Railway dashboard
2. Click "Logs" tab
3. Filter by time, search, or download

**Via CLI**:
```bash
railway login
railway link  # Link to your project
railway logs  # Tail logs
railway logs --service backend  # Specific service
```

### Metrics

Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request count
- Response time

Access via service → Metrics tab

### Alerts

Set up alerts in Railway dashboard:
1. Go to service → Settings → Notifications
2. Configure alerts for:
   - Deployment failures
   - Health check failures
   - High resource usage

## Troubleshooting

### Backend won't start

**Check**:
- Environment variables are set correctly
- `SECRET_KEY` is generated and set
- `DATABASE_URL` is available (add PostgreSQL service)
- `REDIS_URL` is available (add Redis service)
- Dockerfile builds successfully locally
- Health check endpoint `/health` works

**View logs**:
```bash
railway logs --service backend
```

### Frontend shows blank page

**Check**:
- `VITE_API_URL` is set correctly (build-time variable!)
- Backend URL is correct and accessible
- Build completed successfully
- Browser console for errors
- CORS is configured on backend

**Rebuild frontend**:
```bash
railway service  # Select frontend
railway up --detach  # Force rebuild
```

### Database connection errors

**Check**:
- PostgreSQL service is running
- `DATABASE_URL` environment variable is set
- Network connectivity between services
- Database migrations ran successfully

**Run migrations manually**:
```bash
railway run alembic upgrade head
```

### CORS errors

**Fix**:
1. Update `CORS_ORIGINS` in backend environment variables
2. Include frontend Railway domain: `https://your-frontend.up.railway.app`
3. Redeploy backend (Railway will auto-deploy on variable change)

### High memory usage

**Solutions**:
- Reduce `WORKERS` environment variable (default 4)
- Upgrade Railway plan for more resources
- Optimize database queries
- Add caching with Redis

## Cost Optimization

Railway free tier includes:
- $5 credit per month
- Pay for usage beyond that

**Tips to reduce costs**:
1. Use fewer workers (`WORKERS=1` or `WORKERS=2`)
2. Use smaller database instances
3. Enable sleep mode for non-production services
4. Remove unnecessary services
5. Monitor usage in Railway dashboard

## Security Best Practices

1. **Never commit secrets** - Use Railway's environment variables
2. **Rotate SECRET_KEY periodically** - Update in Railway dashboard
3. **Use strong database passwords** - Railway generates these
4. **Enable HTTPS only** - Railway provides SSL automatically
5. **Restrict CORS origins** - Only allow your frontend domain
6. **Monitor logs** - Watch for suspicious activity
7. **Keep dependencies updated** - Railway rebuilds on push
8. **Use Railway's built-in secrets** - Don't expose via public env vars

## Useful Railway CLI Commands

```bash
# Login and link project
railway login
railway link

# View and manage services
railway status
railway service  # Select a service

# Environment variables
railway variables
railway variables set KEY=value
railway variables unset KEY

# Deployments
railway up  # Deploy current directory
railway up --detach  # Deploy and return immediately
railway logs  # View logs
railway logs --service backend  # Service-specific logs

# Database access
railway run psql $DATABASE_URL  # Connect to PostgreSQL
railway run redis-cli -u $REDIS_URL  # Connect to Redis

# Run one-off commands
railway run alembic upgrade head  # Run migrations
railway run python -c "from app.core.security import get_password_hash; print(get_password_hash('test'))"
```

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status Page](https://status.railway.app/)
- [Railway Pricing](https://railway.app/pricing)
- [Environment Variables Guide](https://docs.railway.app/develop/variables)
- [Custom Domains Guide](https://docs.railway.app/deploy/exposing-your-app)

## Support

For Railway-specific issues:
- Check [Railway Docs](https://docs.railway.app/)
- Ask in [Railway Discord](https://discord.gg/railway)
- Contact Railway support via dashboard

For application-specific issues:
- Check application logs in Railway
- Review [CLAUDE.md](./CLAUDE.md) for architecture
- Check [CHANGELOG.md](./CHANGELOG.md) for recent changes
- Open an issue in the project repository
