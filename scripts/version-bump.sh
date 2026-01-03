#!/usr/bin/env bash

# Version bump script
# Usage: ./scripts/version-bump.sh [patch|minor|major]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$PROJECT_ROOT/VERSION"
BACKEND_PYPROJECT="$PROJECT_ROOT/backend/pyproject.toml"
FRONTEND_PACKAGE_JSON="$PROJECT_ROOT/frontend/package.json"

# Check if VERSION file exists
if [ ! -f "$VERSION_FILE" ]; then
    echo -e "${RED}Error: VERSION file not found at $VERSION_FILE${NC}"
    exit 1
fi

# Read current version
CURRENT_VERSION=$(cat "$VERSION_FILE")
echo -e "${YELLOW}Current version: $CURRENT_VERSION${NC}"

# Parse version components
if [[ ! $CURRENT_VERSION =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    echo -e "${RED}Error: Invalid version format in VERSION file. Expected: X.Y.Z${NC}"
    exit 1
fi

MAJOR="${BASH_REMATCH[1]}"
MINOR="${BASH_REMATCH[2]}"
PATCH="${BASH_REMATCH[3]}"

# Determine bump type
BUMP_TYPE="${1:-}"
if [ -z "$BUMP_TYPE" ]; then
    echo -e "${RED}Error: Bump type not specified${NC}"
    echo "Usage: $0 [patch|minor|major]"
    echo ""
    echo "Examples:"
    echo "  $0 patch  # 0.1.0 -> 0.1.1"
    echo "  $0 minor  # 0.1.0 -> 0.2.0"
    echo "  $0 major  # 0.1.0 -> 1.0.0"
    exit 1
fi

# Calculate new version
case "$BUMP_TYPE" in
    patch)
        NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
        ;;
    minor)
        NEW_VERSION="$MAJOR.$((MINOR + 1)).0"
        ;;
    major)
        NEW_VERSION="$((MAJOR + 1)).0.0"
        ;;
    *)
        echo -e "${RED}Error: Invalid bump type '$BUMP_TYPE'${NC}"
        echo "Valid types: patch, minor, major"
        exit 1
        ;;
esac

echo -e "${GREEN}New version: $NEW_VERSION${NC}"
echo ""

# Update VERSION file
echo -e "${YELLOW}Updating VERSION file...${NC}"
echo "$NEW_VERSION" > "$VERSION_FILE"
echo -e "${GREEN}✓ VERSION file updated${NC}"

# Update backend pyproject.toml
if [ -f "$BACKEND_PYPROJECT" ]; then
    echo -e "${YELLOW}Updating backend/pyproject.toml...${NC}"
    # Use sed to update version in pyproject.toml
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" "$BACKEND_PYPROJECT"
    else
        # Linux
        sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" "$BACKEND_PYPROJECT"
    fi
    echo -e "${GREEN}✓ backend/pyproject.toml updated${NC}"
else
    echo -e "${YELLOW}⚠ backend/pyproject.toml not found, skipping${NC}"
fi

# Update frontend package.json
if [ -f "$FRONTEND_PACKAGE_JSON" ]; then
    echo -e "${YELLOW}Updating frontend/package.json...${NC}"
    # Use sed to update version in package.json
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" "$FRONTEND_PACKAGE_JSON"
    else
        # Linux
        sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" "$FRONTEND_PACKAGE_JSON"
    fi
    echo -e "${GREEN}✓ frontend/package.json updated${NC}"
else
    echo -e "${YELLOW}⚠ frontend/package.json not found, skipping${NC}"
fi

echo ""
echo -e "${GREEN}Version bumped from $CURRENT_VERSION to $NEW_VERSION${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git diff"
echo "  2. Commit the changes: git add -A && git commit -m 'chore: bump version to $NEW_VERSION'"
echo "  3. Create a release: ./scripts/release.sh"
