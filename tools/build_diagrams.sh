#!/usr/bin/env bash
# ==============================================================================
# Script de automação para compilação de diagramas Mermaid (.mmd -> .svg / .png)
# com tema Cyberpunk.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"
python3 "$SCRIPT_DIR/build_diagrams.py" "$@"
