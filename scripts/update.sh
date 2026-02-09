#!/bin/bash

# Colors
GREEN='\033[38;2;67;227;39m'
RESET='\033[0m'
BOLD='\033[1m'

# Configuration
REPO="htmlgxn/comfy-imageboard-explorer"
INSTALL_DIR="$HOME/.local/share/imgboard-explorer"

# Functions
print_header() {
    echo -e "${GREEN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║        comfy-imageboard-explorer Updater                 ║"
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
    echo -e "\033[31m✗${RESET} $1"
}

print_info() {
    echo -e "${GREEN}ℹ${RESET} $1"
}

get_installed_version() {
    if [ -f "$INSTALL_DIR/current/VERSION" ]; then
        cat "$INSTALL_DIR/current/VERSION"
    else
        echo ""
    fi
}

get_latest_version() {
    curl -s "https://api.github.com/repos/${REPO}/releases/latest" | grep -o '"tag_name": "[^"]*"' | cut -d'"' -f4
}

update() {
    print_header
    
    # Check if installed
    if [ ! -d "$INSTALL_DIR" ]; then
        print_error "${APP_NAME} is not installed"
        echo ""
        print_info "Install with:"
        echo "  curl -sSL https://raw.githubusercontent.com/${REPO}/main/scripts/install.sh | bash"
        exit 1
    fi
    
    INSTALLED_VERSION=$(get_installed_version)
    if [ -z "$INSTALLED_VERSION" ]; then
        print_error "Could not determine installed version"
        print_step "Reinstalling..."
        exec bash -c "curl -sSL https://raw.githubusercontent.com/${REPO}/main/scripts/install.sh | bash"
    fi
    
    print_info "Installed version: ${INSTALLED_VERSION}"
    
    # Check for latest
    print_step "Checking for updates..."
    LATEST_VERSION=$(get_latest_version)
    
    if [ -z "$LATEST_VERSION" ]; then
        print_error "Could not check for updates"
        exit 1
    fi
    
    if [ "$INSTALLED_VERSION" = "$LATEST_VERSION" ]; then
        print_success "Already up to date (${LATEST_VERSION})"
        exit 0
    fi
    
    print_info "New version available: ${LATEST_VERSION}"
    echo ""
    
    # Run installer
    exec bash -c "curl -sSL https://raw.githubusercontent.com/${REPO}/main/scripts/install.sh | bash"
}

# Run update
update
