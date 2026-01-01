# Environment Architecture Documentation

This document describes the complete environment strategy for the backend application, covering development, testing, and production deployments. This serves as the authoritative reference for all developers and automated systems working with this codebase.

## Philosophy and Core Principles

Our environment strategy is built on three fundamental principles that guide all our architectural decisions. First, we maintain strict environment isolation to ensure that development work never impacts production systems and test runs never interfere with development data. Second, we embrace progressive complexity, meaning our environments become more sophisticated as we move from development to production, with each environment having exactly the infrastructure it needs and no more. Third, we prioritize reproducibility, ensuring that anyone who clones this repository can immediately run the application locally and that our deployment processes are deterministic and repeatable.

Understanding why we separate environments this way is important. Development environments prioritize developer experience with fast iteration cycles and comprehensive debugging tools. Test environments prioritize consistency and isolation to ensure reliable automated testing. Production environments prioritize reliability, security, and performance to serve real users. These different priorities drive different architectural choices for each environment.

## Environment Overview

We maintain three distinct environments throughout our application lifecycle. The development environment runs locally on developer machines using Docker Compose and provides hot reload capabilities for rapid iteration. The test environment also runs locally using Docker Compose with a separate profile and provides isolated, ephemeral databases for automated testing. The production environment runs on Railway's managed infrastructure and handles real user traffic with managed databases and automatic scaling.

We have deliberately chosen not to implement a separate staging environment at this time. Instead, we rely on thorough local testing and Railway's preview deployments for validating changes before they reach production. As the project grows and the team expands, we may revisit this decision and introduce a staging environment that mirrors production infrastructure.

## Development Environment

The development environment is where all feature development and debugging happens. This environment runs entirely on the developer's local machine and is designed to provide the fastest possible feedback loop between writing code and seeing results.

### Technical Implementation

Development uses Docker Compose to orchestrate three core services. PostgreSQL 18 runs on the Debian Trixie base image to match the developer's preference for Debian-based systems. Redis 7 provides caching capabilities and also runs on Debian Bookworm for consistency. The FastAPI backend runs using uvicorn with the reload flag enabled, which watches for file changes and automatically restarts the server when code is modified.

The Docker Compose configuration for development includes volume mounts that enable hot reload functionality. The entire backend directory is mounted into the container so that changes to Python files on the host machine immediately appear inside the container. However, we explicitly exclude the virtual environment directory from this mount to prevent conflicts between the host's Python environment and the container's Python environment. This is crucial because the host might be running a different Python version or have different packages installed, and we want the container's environment to be authoritative.

Data persistence in development is handled through Docker named volumes. Both PostgreSQL and Redis use volumes to store their data, which means that when you stop and restart your development environment, your data remains intact. This allows you to build up test data manually and experiment with your application without having to recreate everything after each restart. If you want to start fresh with a clean database, you can explicitly remove the volumes using Docker Compose down with the volumes flag.

### Configuration and Secrets

Development configuration comes from a file called backend/.env that each developer creates on their local machine. This file is never committed to version control because it contains connection strings and credentials that are specific to each developer's setup. We provide a backend/.env.example file in the repository that documents all required environment variables with placeholder values, making it easy for new developers to set up their local environment.

The secrets in the development environment are low-value secrets that protect only local resources. Your development database password protects a database that runs on your laptop and contains only test data you've created yourself. These secrets should still be kept out of version control to maintain good habits and prevent confusion, but the security implications of these secrets leaking are minimal since they only grant access to your local development containers.

### Development Workflow

A typical development workflow begins with starting the environment using make dev or docker-compose up. This brings up all three services with PostgreSQL and Redis starting first and the backend waiting for them to be healthy before starting. Once the services are running, you can access the API at localhost:8000 and view the automatically generated API documentation at localhost:8000/api/v1/docs.

When you make changes to your Python code, uvicorn detects the changes and automatically reloads the server. You see the new behavior immediately without manually restarting anything. When you need to make database schema changes, you use Alembic to generate and apply migrations, which we'll cover in detail in the database migrations section.

You can connect directly to your development database using any PostgreSQL client by connecting to localhost:5432 with the credentials from your .env file. This is useful for inspecting data, running manual queries, or debugging issues. Similarly, you can connect to Redis at localhost:6379 for cache inspection.

### VSCode Integration

For developers using VSCode, the Python extension needs to know which Python interpreter to use. After running uv sync to create your virtual environment, you configure VSCode to use the interpreter at backend/.venv/bin/python. You can set this through the command palette by searching for Python: Select Interpreter, or by adding configuration to .vscode/settings.json that points to the virtual environment path.

The key insight here is that even though you run your application in Docker containers during development, your editor still benefits from having access to the virtual environment on your host machine. This enables features like autocomplete, type checking, and inline documentation. The virtual environment on your host doesn't need to match the container's environment perfectly, it just needs to have the packages installed so your editor can provide intelligent assistance.

## Test Environment

The test environment exists solely for running automated tests. This environment is completely isolated from development to ensure that tests run against a clean, known state every time. Tests should be deterministic and reproducible, which requires that each test run starts with exactly the same conditions.

### Technical Implementation

The test environment uses Docker Compose profiles to share infrastructure configuration with development while maintaining complete isolation. When you run docker-compose up without any profile flags, only the development services start. When you run docker-compose --profile test up, a completely separate set of services starts with different names, different networks, and different ports.

The test PostgreSQL service uses the same postgres:18-trixie image as development but runs on a different host port to avoid conflicts. Where development PostgreSQL binds to port 5432, test PostgreSQL binds to port 5433. This means you could theoretically run both environments simultaneously, though in practice you rarely need to. The critical difference is that the test PostgreSQL service has no volume mount. When the test container stops, all data is lost. This is intentional. Every time you run tests, you want to start with a completely empty database that your test fixtures populate with known data.

The test backend service also differs from development in its command. Instead of running uvicorn with hot reload, it runs pytest and then exits. The docker-compose configuration uses the --abort-on-container-exit flag, which means that when pytest finishes and the backend container stops, all other test services stop as well. Combined with --exit-code-from backend_test, this returns pytest's exit code to the shell, allowing CI systems to detect whether tests passed or failed.

### Test Configuration and Secrets

Test secrets are hardcoded directly in the docker-compose.yml file, and this is the correct approach. The test database password is literally the string "test_password" right there in the compose file that gets committed to git. This seems wrong if you're thinking about production security practices, but it's actually correct for test environments.

The reason this works is that test secrets protect nothing of value. The test database exists for maybe thirty seconds while tests run, contains only synthetic data that your tests generate, runs on your local machine with no external access, and is destroyed immediately after tests complete. If someone somehow obtained your test database password, what could they do with it? Nothing. The database they would be trying to access doesn't exist ninety-nine percent of the time, and when it does exist, it contains only fake data.

Hardcoding test secrets provides significant benefits. Every developer gets identical test configuration automatically. There's no setup step, no copying of example files, no potential for configuration drift between developers. When a test fails, you know exactly what credentials were used and can easily reproduce the failure. Your CI system can use the exact same configuration without any secret management overhead.

The test environment sets a TESTING environment variable to true, which your application code can check to enable test-specific behavior if needed. For example, you might disable certain external API calls in test mode or use mock services instead of real ones.

### Test Workflow and Pytest Configuration

Running tests is a single command: make test or docker-compose --profile test up --abort-on-container-exit. This starts the test services, runs pytest inside the test backend container, and stops everything when tests complete. The test output appears in your terminal, showing which tests passed or failed.

Pytest is configured through backend/pytest.ini to discover tests in the tests directory and run them with appropriate verbosity and async support. The critical test fixtures live in backend/tests/conftest.py and handle database lifecycle. Each test function receives a fresh database through the db_session fixture. This fixture creates all tables before the test runs, provides a database session to the test code, and drops all tables after the test completes. This ensures complete isolation between tests.

This approach is slower than using database transactions with rollback, but it's more robust. It truly isolates each test and ensures that side effects from one test cannot affect another. For a young project, this robustness is more valuable than the performance difference. As your test suite grows and performance becomes a concern, you can optimize this strategy, but starting with complete isolation gives you the most reliable foundation.

## Production Environment

The production environment runs on Railway's managed infrastructure and serves real users. This environment prioritizes reliability, security, and performance over developer convenience. Every architectural decision in production is made with these priorities in mind.

### Railway Platform Overview

Railway is a managed platform that handles infrastructure concerns so you can focus on your application code. When you deploy to Railway, you push your code to a git repository, Railway automatically builds your Docker image using your production Dockerfile, deploys the image to their infrastructure, manages SSL certificates for your custom domain, provides managed PostgreSQL and Redis instances, handles environment variable and secrets management, automatically restarts failed containers, and provides basic monitoring and logging.

The key advantage of Railway over self-hosting is that you avoid the operational overhead of managing servers, configuring firewalls, handling SSL certificate renewal, setting up monitoring, managing backups, and dealing with security patches. The trade-off is cost and some loss of control, but for a young project, the time savings are usually worth the cost.

### Production Architecture

Your production deployment consists of several components working together. Your FastAPI backend runs as a Railway service with multiple worker processes for handling concurrent requests. The managed PostgreSQL database provided by Railway runs on their infrastructure with automatic backups and high availability. The managed Redis instance also runs on Railway's infrastructure for caching. Railway's load balancer sits in front of your backend service, handling SSL termination and routing traffic. The platform's logging infrastructure captures all container output for debugging and monitoring.

The production Dockerfile differs significantly from the development Dockerfile in ways that reflect production priorities. It uses a multi-stage build where the first stage has all build dependencies and the second stage contains only runtime requirements, minimizing the final image size. The image runs as a non-root user for security rather than as root. It uses multiple uvicorn workers instead of a single worker with hot reload, enabling concurrent request handling. It uses the slim variant of the Python base image to reduce attack surface and image size. It includes a health check endpoint that Railway uses to determine if the container is healthy.

### Production Configuration and Secrets

Production configuration comes entirely from environment variables that you configure in Railway's dashboard or CLI. These environment variables include the database URL that Railway provides when you add a PostgreSQL database to your project, the Redis URL from Railway's Redis addon, a cryptographically strong secret key generated with openssl rand -hex 32, CORS origins listing your production frontend domain, and any other application-specific configuration.

Production secrets are managed through Railway's secrets system. You configure these through Railway's web interface, and they are encrypted at rest and in transit. The secrets are injected into your container as environment variables at runtime, never appearing in your codebase or Docker images. This is the correct way to handle production secrets because it keeps them completely separate from code, allows rotation without code changes, provides audit logs of who accessed or modified secrets, and ensures secrets never end up in version control or logs.

The critical principle here is that production secrets have real value. Your production database password protects real user data. Your JWT secret key is used to sign authentication tokens for real users. If these secrets leak, the security implications are serious. This is why production secrets require careful management and why the approach differs completely from test secrets.

### Database Migrations in Production

Database migrations in production require careful handling to avoid downtime or data loss. Railway supports deployment lifecycle hooks that let you run commands before your new application code starts. You configure a release command in Railway's settings to run alembic upgrade head before each deployment. This ensures that database schema changes are applied before the new code that depends on those changes begins running.

The critical consideration for production migrations is backwards compatibility. You cannot deploy a migration that removes a database column and code that stops using that column in a single deployment because there will be a moment during the rolling deployment where old code tries to access the column that the migration just removed. The correct approach is to deploy changes in phases. First, deploy code that stops using a column but doesn't remove it. Verify everything works. Then deploy a second change that actually removes the column from the database. This ensures zero-downtime deployments.

Similarly, when adding a column, you should add it as nullable initially even if it will eventually be required. Deploy the migration that adds the nullable column, verify everything works, backfill the column with appropriate values if needed, and then deploy another migration that makes the column non-nullable. This multi-phase approach keeps your database schema compatible with both old and new code during deployment transitions.

### Deployment Workflow

The production deployment workflow follows a git-based approach. You develop features on feature branches in your local environment, running and testing everything locally. When a feature is complete, you merge it to your main branch through a pull request. Railway watches your main branch for changes, so when the merge happens, Railway automatically triggers a deployment.

During deployment, Railway builds your production Docker image using the Dockerfile in your repository. It runs your database migrations using the release command you configured. It starts new containers with the new image while old containers continue serving traffic. It waits for new containers to pass health checks before routing traffic to them. Once new containers are healthy and receiving traffic, it stops the old containers. If health checks fail, it aborts the deployment and keeps the old version running.

This rolling deployment process means users experience no downtime. At any moment during deployment, some version of your application is running and serving requests. The deployment either completes successfully with the new version, or it fails and automatically rolls back to the old version.

Railway also provides preview deployments for pull requests. When you open a pull request, Railway can automatically deploy that branch to a temporary environment with its own database and URL. This lets you test changes in a production-like environment before merging to main. Once the pull request is closed, the preview environment is destroyed.

### Monitoring and Logging

Railway provides basic logging that captures all output from your containers. You can view these logs in Railway's dashboard or retrieve them via their CLI. For more sophisticated monitoring, you would integrate a service like Sentry for error tracking or Datadog for metrics and traces. These integrations are typically configured through environment variables that tell your application where to send monitoring data.

Your FastAPI application should include structured logging that helps you understand what's happening in production. Instead of print statements, use Python's logging module to emit structured log messages with appropriate severity levels. In production, these logs flow to Railway's logging infrastructure where you can search and analyze them.

The health check endpoint at /health is critical for monitoring. Railway hits this endpoint regularly to determine if your container is healthy. If the health check fails repeatedly, Railway considers the container unhealthy and restarts it. Your health check should verify that your application can connect to its dependencies, particularly the database, and return a simple JSON response indicating health status.

## Environment Comparison Matrix

To summarize the key differences between environments, consider these dimensions. For infrastructure management, development uses Docker Compose on localhost, test uses Docker Compose with profiles on localhost, and production uses Railway's managed infrastructure. For data persistence, development data survives restarts through Docker volumes, test data is completely ephemeral and destroyed after each run, and production data is managed by Railway's PostgreSQL with automatic backups.

For secrets management, development uses local .env files that are gitignored, test uses hardcoded secrets in docker-compose.yml, and production uses Railway's encrypted secrets system. For database migrations, development applies migrations manually using Alembic CLI, test creates and drops all tables for each test run, and production runs migrations automatically via Railway's release command.

For deployment process, development involves running docker-compose up on your machine, test involves running make test or the equivalent docker-compose command, and production is triggered automatically by pushing to the main branch. For external access, development services are available on localhost ports, test services are isolated with no external access needed, and production services are available at your production domain with SSL.

## Docker Compose Configuration Strategy

Our docker-compose.yml file uses profiles to support both development and test environments in a single file. Services without a profile tag run by default, which means running docker-compose up starts the development environment. Services tagged with profiles: ["test"] only start when you use docker-compose --profile test up, which gives you the isolated test environment.

This profile-based approach keeps all local environment configuration in one place, making it easy to see how the environments differ and reducing the risk of configuration drift. Both environments share the same base service definitions where appropriate, but differ in details like database persistence, port bindings, and service commands.

The networks are also separated by profile. Development services use a backend_network, while test services use a test_network. This network isolation ensures that even if you run both environments simultaneously, they cannot communicate with each other. Development PostgreSQL and test PostgreSQL are completely independent.

## Working with Multiple Environments

When working on this project, you will regularly interact with all three environments in a typical development cycle. You start by working in development, where you run make dev to start your local environment, make code changes and see them reflected immediately through hot reload, manually test your changes through the API documentation at localhost:8000/api/v1/docs, and create database migrations when you modify models.

Before committing your changes, you run tests locally by executing make test to start the test environment and run pytest. This ensures your changes haven't broken existing functionality and that any new features you added have tests covering them. You review the test output, debug any failures, and iterate until all tests pass.

Once tests pass locally and you're satisfied with your changes, you commit your code and push to your feature branch. When you're ready to deploy, you merge your feature branch to main through a pull request. Railway detects the merge and automatically deploys to production, running migrations and starting the new version of your application. You monitor the deployment in Railway's dashboard and verify that health checks pass and the new version is serving traffic correctly.

This workflow ensures that every change goes through all three environments in order. You develop locally with fast iteration, validate with automated tests in isolation, and deploy to production with confidence that the code has been tested. Each environment serves its specific purpose in this progression.

## Best Practices and Guidelines

Several practices will help you work effectively with this environment architecture. Always test locally before pushing to production, using make test to run your full test suite before committing changes. Never commit secrets to version control, keeping .env files gitignored and using Railway's secrets system for production. Use explicit versioning for production deployments through git tags or semantic versioning in your commit messages.

When writing code, use environment variables for all configuration rather than hardcoding values, which makes your application portable across environments. Log appropriately for each environment, using debug-level logs in development that would be too verbose for production. Write backwards-compatible database migrations that allow zero-downtime deployments. Regularly backup production data through Railway's backup features and verify that you can restore from backups.

Understanding these best practices and the reasoning behind them will help you maintain a healthy separation between environments while keeping your workflow smooth and your deployments reliable. This document should serve as your reference whenever you have questions about where something should run or how configuration should be managed. As the project evolves, update this document to reflect new practices and architectural decisions.