# Build stage
FROM node:24-alpine AS builder

# Accept build arguments
ARG VERSION=0.0.0
ARG VITE_API_URL=http://localhost:8000

WORKDIR /app

# Set environment variables for build
# Vite will read these during the build process
ENV VERSION=${VERSION}
ENV VITE_API_URL=${VITE_API_URL}

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
# Vite bakes VITE_* env vars into the build
RUN npm run build

# Production stage
FROM nginx:alpine

# Accept version as build argument in final stage
ARG VERSION=0.0.0

# Add version metadata to the image
LABEL org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.title="Frontend" \
      org.opencontainers.image.description="React frontend application"

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
