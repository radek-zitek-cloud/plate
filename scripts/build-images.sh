#!/usr/bin/env bash

# Docker image build script with version tagging
# Builds production Docker images with proper version tags
# Usage: ./scripts/build-images.sh [--push] [--registry REGISTRY]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$PROJECT_ROOT/VERSION"

# Check if VERSION file exists
if [ ! -f "$VERSION_FILE" ]; then
    echo -e "${RED}Error: VERSION file not found at $VERSION_FILE${NC}"
    exit 1
fi

# Read current version
VERSION=$(cat "$VERSION_FILE")
echo -e "${BLUE}Building images for version: $VERSION${NC}"
echo ""

# Parse command line arguments
PUSH=false
REGISTRY="localhost"

while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH=true
            shift
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Error: Unknown argument $1${NC}"
            echo "Usage: $0 [--push] [--registry REGISTRY]"
            exit 1
            ;;
    esac
done

# Export VERSION for docker-compose
export VERSION
export DOCKER_REGISTRY="$REGISTRY"

# Build backend image
echo -e "${YELLOW}Building backend image...${NC}"
docker build \
    --build-arg VERSION="$VERSION" \
    -t "$REGISTRY/backend:$VERSION" \
    -t "$REGISTRY/backend:latest" \
    -f "$PROJECT_ROOT/backend/Dockerfile" \
    "$PROJECT_ROOT/backend"
echo -e "${GREEN}✓ Backend image built${NC}"
echo ""

# Build frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
docker build \
    --build-arg VERSION="$VERSION" \
    -t "$REGISTRY/frontend:$VERSION" \
    -t "$REGISTRY/frontend:latest" \
    -f "$PROJECT_ROOT/frontend/Dockerfile" \
    "$PROJECT_ROOT/frontend"
echo -e "${GREEN}✓ Frontend image built${NC}"
echo ""

# List built images
echo -e "${BLUE}Built images:${NC}"
docker images | grep -E "($REGISTRY/backend|$REGISTRY/frontend)" | grep -E "($VERSION|latest)" || true
echo ""

# Push images if requested
if [ "$PUSH" = true ]; then
    echo -e "${YELLOW}Pushing images to registry $REGISTRY...${NC}"
    echo ""

    echo -e "${YELLOW}Pushing backend:$VERSION...${NC}"
    docker push "$REGISTRY/backend:$VERSION"
    echo -e "${GREEN}✓ Pushed backend:$VERSION${NC}"

    echo -e "${YELLOW}Pushing backend:latest...${NC}"
    docker push "$REGISTRY/backend:latest"
    echo -e "${GREEN}✓ Pushed backend:latest${NC}"

    echo -e "${YELLOW}Pushing frontend:$VERSION...${NC}"
    docker push "$REGISTRY/frontend:$VERSION"
    echo -e "${GREEN}✓ Pushed frontend:$VERSION${NC}"

    echo -e "${YELLOW}Pushing frontend:latest...${NC}"
    docker push "$REGISTRY/frontend:latest"
    echo -e "${GREEN}✓ Pushed frontend:latest${NC}"

    echo ""
    echo -e "${GREEN}All images pushed successfully!${NC}"
else
    echo -e "${YELLOW}Images built but not pushed to registry${NC}"
    echo "To push images, run:"
    echo "  $0 --push --registry $REGISTRY"
fi

echo ""
echo -e "${GREEN}Build complete!${NC}"
