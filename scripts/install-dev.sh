#!/bin/bash
# Thin wrapper for dev install - delegates to install.sh with --dev flag
exec bash -c 'curl -sSL https://raw.githubusercontent.com/htmlgxn/imageboard-explorer/main/scripts/install.sh | bash -s -- --dev "$@"' bash "$@"
