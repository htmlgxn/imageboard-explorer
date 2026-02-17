#!/bin/bash

# Colors
GREEN='\033[38;2;67;227;39m'
RESET='\033[0m'
BOLD='\033[1m'
RED='\033[31m'

# Configuration
REPO="htmlgxn/imageboard-explorer"
INSTALL_DIR="$HOME/.local/share/imageboard-explorer"
BIN_DIR="$HOME/.local/bin"
APP_NAME="imageboard-explorer"
DEFAULT_DEV_DIR="$HOME/projects/imageboard-explorer"

# Parse arguments
DEV_MODE=false
UNINSTALL_MODE=false

for arg in "$@"; do
	case $arg in
	--dev)
		DEV_MODE=true
		shift
		;;
	--uninstall)
		UNINSTALL_MODE=true
		shift
		;;
	esac
done

# Functions
print_header() {
	echo -e "${GREEN}${BOLD}"
	echo "╔══════════════════════════════════════════════════════════╗"
	if [ "$DEV_MODE" = true ]; then
		echo "║     imageboard-explorer Dev Installer              ║"
	else
		echo "║        imageboard-explorer Installer               ║"
	fi
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

print_prompt() {
	echo -e "${GREEN}?${RESET} $1"
}

check_uv() {
	if ! command -v uv &>/dev/null; then
		print_error "uv is not installed"
		echo ""
		echo "Please install uv first:"
		echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
		echo ""
		echo "Or visit: https://docs.astral.sh/uv/getting-started/installation/"
		exit 1
	fi
	print_success "uv is installed"
}

check_git() {
	if ! command -v git &>/dev/null; then
		print_error "git is not installed"
		exit 1
	fi
	print_success "git is installed"
}

get_latest_version() {
	print_step "Checking for latest version..."
	LATEST_VERSION=$(curl -s "https://api.github.com/repos/${REPO}/releases/latest" | grep -o '"tag_name": "[^"]*"' | cut -d'"' -f4)
	if [ -z "$LATEST_VERSION" ]; then
		print_error "Could not determine latest version"
		exit 1
	fi
	print_success "Latest version: ${LATEST_VERSION}"
}

check_existing_install() {
	if [ -L "$BIN_DIR/$APP_NAME" ] || [ -d "$INSTALL_DIR" ]; then
		return 0
	fi
	return 1
}

check_existing_dev() {
	if [ -d "$DEFAULT_DEV_DIR/.git" ] || [ -L "$BIN_DIR/${APP_NAME}-dev" ]; then
		return 0
	fi
	# Also check if DEV_DIR env var is set and exists
	if [ -n "$DEV_DIR" ] && [ -d "$DEV_DIR/.git" ]; then
		return 0
	fi
	return 1
}

get_installed_version() {
	if [ -f "$INSTALL_DIR/current/VERSION" ]; then
		cat "$INSTALL_DIR/current/VERSION"
	else
		echo "unknown"
	fi
}

get_dev_directory() {
	# If DEV_DIR is set via environment variable, use it
	if [ -n "$DEV_DIR" ]; then
		echo "$DEV_DIR"
		return
	fi

	# Otherwise, prompt the user
	local dev_dir="$DEFAULT_DEV_DIR"

	echo ""
	print_prompt "Clone to ${dev_dir}? [Y/n] "
	read -r response

	if [[ "$response" =~ ^[Nn]$ ]]; then
		echo ""
		print_prompt "Enter directory path: "
		read -r custom_dir
		if [ -n "$custom_dir" ]; then
			# Expand ~ to $HOME if present
			dev_dir="${custom_dir/#\~/$HOME}"
		fi
	fi

	echo "$dev_dir"
}

uninstall_regular() {
	local found=false

	# Remove symlink
	if [ -L "$BIN_DIR/$APP_NAME" ]; then
		rm "$BIN_DIR/$APP_NAME"
		print_success "Removed symlink from ${BIN_DIR}"
		found=true
	fi

	# Remove installation directory
	if [ -d "$INSTALL_DIR" ]; then
		rm -rf "$INSTALL_DIR"
		print_success "Removed installation directory"
		found=true
	fi

	if [ "$found" = true ]; then
		return 0
	fi
	return 1
}

uninstall_dev() {
	local found=false
	local dev_dirs=("$DEFAULT_DEV_DIR")

	# Check if DEV_DIR was set
	if [ -n "$DEV_DIR" ]; then
		dev_dirs+=("$DEV_DIR")
	fi

	# Remove dev symlink
	if [ -L "$BIN_DIR/${APP_NAME}-dev" ]; then
		rm "$BIN_DIR/${APP_NAME}-dev"
		print_success "Removed dev symlink from ${BIN_DIR}"
		found=true
	fi

	# Remove dev directories
	for dev_dir in "${dev_dirs[@]}"; do
		if [ -d "$dev_dir/.git" ] || [ -d "$dev_dir" ]; then
			print_info "Removing ${dev_dir}..."
			rm -rf "$dev_dir"
			print_success "Removed development directory: ${dev_dir}"
			found=true
		fi
	done

	if [ "$found" = true ]; then
		return 0
	fi
	return 1
}

uninstall() {
	print_header
	print_step "Uninstalling ${APP_NAME}..."
	echo ""

	local regular_uninstalled=false
	local dev_uninstalled=false

	# Try to uninstall regular version
	if uninstall_regular; then
		regular_uninstalled=true
	fi

	# Try to uninstall dev version
	if uninstall_dev; then
		dev_uninstalled=true
	fi

	echo ""
	if [ "$regular_uninstalled" = true ] || [ "$dev_uninstalled" = true ]; then
		print_success "${APP_NAME} has been uninstalled"
	else
		print_info "${APP_NAME} was not installed"
	fi

	echo ""
	print_info "To reinstall:"
	echo "  Regular:  curl -sSL https://raw.githubusercontent.com/${REPO}/main/scripts/install.sh | bash"
	echo "  Dev:      curl -sSL https://raw.githubusercontent.com/${REPO}/main/scripts/install.sh | bash -s -- --dev"
}

install_regular() {
	# Check uv
	check_uv

	# Get latest version
	get_latest_version

	# Check for existing install
	if check_existing_install; then
		INSTALLED_VERSION=$(get_installed_version)
		if [ "$INSTALLED_VERSION" = "$LATEST_VERSION" ]; then
			print_info "${APP_NAME} ${LATEST_VERSION} is already installed and up to date"
			echo ""
			print_info "To reinstall, first uninstall:"
			echo "  curl -sSL https://raw.githubusercontent.com/${REPO}/main/scripts/install.sh | bash -s -- --uninstall"
			exit 0
		else
			print_step "Updating from ${INSTALLED_VERSION} to ${LATEST_VERSION}..."
		fi
	else
		print_step "Installing ${APP_NAME} ${LATEST_VERSION}..."
	fi

	# Create directories
	mkdir -p "$INSTALL_DIR"
	mkdir -p "$BIN_DIR"

	# Download release
	print_step "Downloading release ${LATEST_VERSION}..."
	VERSION_NUM="${LATEST_VERSION#v}"
	DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${LATEST_VERSION}/comfy_imageboard_explorer-${VERSION_NUM}.tar.gz"
	TEMP_DIR=$(mktemp -d)

	if ! curl -sL "$DOWNLOAD_URL" -o "$TEMP_DIR/release.tar.gz"; then
		print_error "Failed to download release"
		rm -rf "$TEMP_DIR"
		exit 1
	fi

	# Extract
	print_step "Extracting files..."
	VERSION_DIR="$INSTALL_DIR/${LATEST_VERSION}"
	mkdir -p "$VERSION_DIR"

	if ! tar -xzf "$TEMP_DIR/release.tar.gz" -C "$VERSION_DIR" --strip-components=1; then
		print_error "Failed to extract release"
		rm -rf "$TEMP_DIR" "$VERSION_DIR"
		exit 1
	fi

	# Save version
	echo "$LATEST_VERSION" >"$VERSION_DIR/VERSION"

	# Update current symlink
	if [ -L "$INSTALL_DIR/current" ]; then
		rm "$INSTALL_DIR/current"
	fi
	ln -s "$VERSION_DIR" "$INSTALL_DIR/current"

	# Create/Update bin symlink
	if [ -L "$BIN_DIR/$APP_NAME" ]; then
		rm "$BIN_DIR/$APP_NAME"
	fi
	ln -s "$INSTALL_DIR/current/scripts/run.sh" "$BIN_DIR/$APP_NAME"

	# Cleanup
	rm -rf "$TEMP_DIR"

	# Clean old versions (keep last 2)
	print_step "Cleaning up old versions..."
	cd "$INSTALL_DIR" && ls -1 | grep -E '^v?[0-9]\.' | sort -V | head -n -2 | xargs -r rm -rf

	# Add to PATH if needed
	if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
		echo ""
		print_info "Adding ${BIN_DIR} to PATH..."

		SHELL_NAME=$(basename "$SHELL")
		case "$SHELL_NAME" in
		bash)
			echo "export PATH=\"$BIN_DIR:\$PATH\"" >>"$HOME/.bashrc"
			;;
		zsh)
			echo "export PATH=\"$BIN_DIR:\$PATH\"" >>"$HOME/.zshrc"
			;;
		fish)
			fish -c "set -Ux PATH $BIN_DIR \$PATH"
			;;
		*)
			echo "export PATH=\"$BIN_DIR:\$PATH\"" >>"$HOME/.profile"
			;;
		esac

		print_info "Please restart your terminal or run:"
		echo "  export PATH=\"$BIN_DIR:\$PATH\""
	fi

	echo ""
	print_success "${APP_NAME} ${LATEST_VERSION} has been installed!"
	echo ""
	print_info "Usage:"
	echo "  ${APP_NAME}                          # Run the application"
	echo "  ${APP_NAME} update                   # Check for updates"
	echo ""
	print_info "To uninstall:"
	echo "  curl -sSL https://raw.githubusercontent.com/${REPO}/main/scripts/install.sh | bash -s -- --uninstall"
}

install_dev() {
	# Check prerequisites
	check_uv
	check_git

	# Get dev directory
	DEV_DIR=$(get_dev_directory)

	print_step "Setting up development environment..."

	# Create parent directory if needed
	PARENT_DIR=$(dirname "$DEV_DIR")
	if [ ! -d "$PARENT_DIR" ]; then
		print_step "Creating parent directory ${PARENT_DIR}..."
		mkdir -p "$PARENT_DIR"
	fi

	# Clone or update repo
	if [ -d "$DEV_DIR/.git" ]; then
		print_step "Updating existing repository..."
		cd "$DEV_DIR"
		git pull
	elif [ -d "$DEV_DIR" ]; then
		# Directory exists but is not a git repo
		print_error "Directory ${DEV_DIR} already exists and is not a git repository"
		echo ""
		print_info "Please remove it first or choose a different directory"
		exit 1
	else
		print_step "Cloning repository to ${DEV_DIR}..."
		git clone "https://github.com/${REPO}.git" "$DEV_DIR"
		if [ $? -ne 0 ]; then
			print_error "Failed to clone repository"
			exit 1
		fi
	fi

	cd "$DEV_DIR"

	# Install dependencies
	print_step "Installing dependencies..."
	if ! uv sync --extra dev; then
		print_error "Failed to install dependencies"
		exit 1
	fi

	# Create bin directory
	mkdir -p "$BIN_DIR"

	# Create dev run script
	print_step "Creating dev launcher..."
	cat >"$DEV_DIR/run-dev.sh" <<EOF
#!/bin/bash
cd "$DEV_DIR" && uv run imageboard-explorer "\$@"
EOF
	chmod +x "$DEV_DIR/run-dev.sh"

	# Create symlink
	if [ -L "$BIN_DIR/${APP_NAME}-dev" ]; then
		rm "$BIN_DIR/${APP_NAME}-dev"
	fi
	ln -s "$DEV_DIR/run-dev.sh" "$BIN_DIR/${APP_NAME}-dev"

	# Add to PATH if needed
	if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
		echo ""
		print_info "Adding ${BIN_DIR} to PATH..."

		SHELL_NAME=$(basename "$SHELL")
		case "$SHELL_NAME" in
		bash)
			echo "export PATH=\"$BIN_DIR:\$PATH\"" >>"$HOME/.bashrc"
			;;
		zsh)
			echo "export PATH=\"$BIN_DIR:\$PATH\"" >>"$HOME/.zshrc"
			;;
		fish)
			fish -c "set -Ux PATH $BIN_DIR \$PATH"
			;;
		*)
			echo "export PATH=\"$BIN_DIR:\$PATH\"" >>"$HOME/.profile"
			;;
		esac

		print_info "Please restart your terminal or run:"
		echo "  export PATH=\"$BIN_DIR:\$PATH\""
	fi

	echo ""
	print_success "Development environment has been set up!"
	echo ""
	print_info "Usage:"
	echo "  ${APP_NAME}-dev                       # Run in dev mode"
	echo "  cd ${DEV_DIR} && uv run pytest       # Run tests"
	echo ""
	print_info "Development directory: ${DEV_DIR}"
	print_info "To update: cd ${DEV_DIR} && git pull"
	echo ""
	print_info "To uninstall:"
	echo "  curl -sSL https://raw.githubusercontent.com/${REPO}/main/scripts/install.sh | bash -s -- --uninstall"
}

# Main execution
main() {
	print_header

	# Check for uninstall flag
	if [ "$UNINSTALL_MODE" = true ]; then
		uninstall
		exit 0
	fi

	# Check for dev flag
	if [ "$DEV_MODE" = true ]; then
		install_dev
		exit 0
	fi

	# Default: regular install
	install_regular
}

main
