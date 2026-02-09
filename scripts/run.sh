#!/bin/bash
# Launcher script for installed imgboard-explorer

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." && exec uv run imgboard-explorer "$@"
