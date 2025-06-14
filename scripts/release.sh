#!/bin/bash
# Script to create a release of the Ansible TinyLlama Integration

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "==========================================================="
echo "          Ansible TinyLlama Release Builder                "
echo "==========================================================="
echo -e "${NC}"

# Check for required tools
for cmd in git docker docker-compose; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}Error: $cmd is required but not installed.${NC}"
        exit 1
    fi
done

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Not in a git repository root directory.${NC}"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}Warning: You have uncommitted changes.${NC}"
    read -p "Continue anyway? (y/N): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        echo "Aborting release process."
        exit 1
    fi
fi

# Get current version from pyproject.toml or other source
if [ -f "pyproject.toml" ]; then
    CURRENT_VERSION=$(grep -E '^version\s*=' pyproject.toml | cut -d'"' -f2 || echo "0.0.0")
else
    CURRENT_VERSION="0.0.0"
fi

echo "Current version: $CURRENT_VERSION"

# Ask for new version
read -p "Enter new version (leave blank to use current): " NEW_VERSION
if [ -z "$NEW_VERSION" ]; then
    NEW_VERSION=$CURRENT_VERSION
fi

# Validate semver format
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Error: Version must be in format X.Y.Z${NC}"
    exit 1
fi

echo "Building release version $NEW_VERSION"

# Update version in files
if [ -f "pyproject.toml" ]; then
    sed -i.bak "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    rm -f pyproject.toml.bak
fi

if [ -f "src/__init__.py" ]; then
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" src/__init__.py
    rm -f src/__init__.py.bak
fi

# Build Docker image
echo "Building Docker image..."
docker build -t ansible-tinyllama:$NEW_VERSION .

# Create release tag
echo "Creating release tag..."
git add -A
git commit -m "build: release version $NEW_VERSION" || true
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

echo -e "${GREEN}"
echo "==========================================================="
echo "Release v$NEW_VERSION created successfully!"
echo "==========================================================="
echo -e "${NC}"

echo "Next steps:"
echo "1. Push the commit: git push origin main"
echo "2. Push the tag: git push origin v$NEW_VERSION"
echo "3. Create a GitHub release"
echo "4. Push Docker image to registry if needed"

# Ask if user wants to push now
read -p "Push commit and tag now? (y/N): " PUSH
if [[ "$PUSH" =~ ^[Yy]$ ]]; then
    git push origin main
    git push origin "v$NEW_VERSION"
    echo -e "${GREEN}Pushed successfully!${NC}"
fi

# Ask if user wants to create GitHub release
if command -v gh &> /dev/null; then
    read -p "Create GitHub release now? (y/N): " CREATE_RELEASE
    if [[ "$CREATE_RELEASE" =~ ^[Yy]$ ]]; then
        # Extract changes from CHANGELOG.md
        if [ -f "CHANGELOG.md" ]; then
            # Extract section for this version
            NOTES=$(sed -n "/## \[$NEW_VERSION\]/,/## \[/p" CHANGELOG.md | sed '1d;$d')
            if [ -z "$NOTES" ]; then
                NOTES="Release version $NEW_VERSION"
            fi
            echo "$NOTES" > /tmp/release_notes.md
            gh release create "v$NEW_VERSION" --title "Release v$NEW_VERSION" --notes-file /tmp/release_notes.md
            rm -f /tmp/release_notes.md
        else
            gh release create "v$NEW_VERSION" --title "Release v$NEW_VERSION"
        fi
        echo -e "${GREEN}GitHub release created!${NC}"
    fi
else
    echo "GitHub CLI not found. If you want to create a GitHub release, install the GitHub CLI or create it manually."
fi
