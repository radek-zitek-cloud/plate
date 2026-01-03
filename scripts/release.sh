#!/usr/bin/env bash

# Release script
# Creates a git tag for the current version and optionally pushes it
# Usage: ./scripts/release.sh [--push]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
TAG="v$VERSION"

echo -e "${YELLOW}Current version: $VERSION${NC}"
echo -e "${YELLOW}Git tag: $TAG${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}Error: You have uncommitted changes${NC}"
    echo "Please commit or stash your changes before creating a release."
    git status --short
    exit 1
fi

# Check if --push flag is provided
PUSH_FLAG="${1:-}"

# Check if tag already exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    # Tag exists - check if we're just trying to push it
    if [ "$PUSH_FLAG" = "--push" ]; then
        echo -e "${YELLOW}Tag $TAG already exists locally${NC}"
        echo -e "${YELLOW}Pushing tag to remote...${NC}"
        git push origin "$TAG"
        echo -e "${GREEN}✓ Tag pushed to remote${NC}"
        echo ""
        echo -e "${GREEN}Release $VERSION complete!${NC}"
        exit 0
    else
        echo -e "${RED}Error: Tag $TAG already exists${NC}"
        echo "If you want to push the existing tag, run:"
        echo "  ./scripts/release.sh --push"
        echo ""
        echo "If you want to create a new release, bump the version first:"
        echo "  ./scripts/version-bump.sh [patch|minor|major]"
        exit 1
    fi
fi

# Create the tag
echo -e "${YELLOW}Creating git tag $TAG...${NC}"
git tag -a "$TAG" -m "Release $VERSION"
echo -e "${GREEN}✓ Tag $TAG created${NC}"

if [ "$PUSH_FLAG" = "--push" ]; then
    echo ""
    echo -e "${YELLOW}Pushing tag to remote...${NC}"
    git push origin "$TAG"
    echo -e "${GREEN}✓ Tag pushed to remote${NC}"
else
    echo ""
    echo -e "${YELLOW}Tag created locally but not pushed to remote${NC}"
    echo "To push the tag, run:"
    echo "  git push origin $TAG"
    echo ""
    echo "Or run this script with --push flag:"
    echo "  ./scripts/release.sh --push"
fi

echo ""
echo -e "${GREEN}Release $VERSION complete!${NC}"
