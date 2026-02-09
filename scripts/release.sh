#!/bin/bash

# Colors
GREEN='\033[38;2;67;227;39m'
RESET='\033[0m'
BOLD='\033[1m'
RED='\033[31m'

# Functions
print_header() {
    echo -e "${GREEN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║        comfy-imageboard-explorer Release Tool            ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${RESET}"
}

print_step() {
    echo -e "${GREEN}→${RESET} $1"
}

print_success() {
    echo -e "${GREEN}✓${RESET} $1"
}

print_error() {
    echo -e "${RED}✗${RESET} $1"
}

print_info() {
    echo -e "${GREEN}ℹ${RESET} $1"
}

print_header

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)

if [ -z "$VERSION" ]; then
    print_error "Could not determine version from pyproject.toml"
    exit 1
fi

echo ""
print_info "Preparing release for version: ${VERSION}"
echo ""

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_error "There are uncommitted changes"
    echo "Please commit or stash changes before releasing"
    exit 1
fi

# Run tests
print_step "Running tests..."
if ! uv run pytest tests/ -v; then
    print_error "Tests failed"
    exit 1
fi
print_success "All tests passed"

# Type check
print_step "Running type checker..."
if ! uv run mypy src/ tests/; then
    print_error "Type checking failed"
    exit 1
fi
print_success "Type checking passed"

# Create release directory
print_step "Creating release archive..."
RELEASE_DIR=$(mktemp -d)
mkdir -p "$RELEASE_DIR/imgboard-explorer-${VERSION}"

# Copy files
print_step "Copying files..."
cp -r src "$RELEASE_DIR/imgboard-explorer-${VERSION}/"
cp -r scripts "$RELEASE_DIR/imgboard-explorer-${VERSION}/"
cp pyproject.toml "$RELEASE_DIR/imgboard-explorer-${VERSION}/"
cp README.md "$RELEASE_DIR/imgboard-explorer-${VERSION}/"
cp LICENSE "$RELEASE_DIR/imgboard-explorer-${VERSION}/"

# Create VERSION file
echo "$VERSION" > "$RELEASE_DIR/imgboard-explorer-${VERSION}/VERSION"

# Create tarball
print_step "Creating tarball..."
cd "$RELEASE_DIR"
tar -czf "imgboard-explorer-${VERSION}.tar.gz" "imgboard-explorer-${VERSION}"

# Move to dist
mkdir -p "$(pwd)/dist"
mv "imgboard-explorer-${VERSION}.tar.gz" "$(pwd)/dist/"

print_success "Created dist/imgboard-explorer-${VERSION}.tar.gz"

# Create GitHub release
print_step "Creating GitHub release..."
echo ""
print_info "To complete the release, run:"
echo ""
echo "  git tag -a v${VERSION} -m 'Release v${VERSION}'"
echo "  git push origin v${VERSION}"
echo ""
echo "  gh release create v${VERSION} dist/imgboard-explorer-${VERSION}.tar.gz \\"
echo "    --title 'v${VERSION}' \\"
echo "    --notes 'Release v${VERSION}'"
echo ""

# Cleanup
rm -rf "$RELEASE_DIR"

print_success "Release preparation complete!"
