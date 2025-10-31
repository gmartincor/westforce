#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MCP_CONFIG_DIR="${HOME}/.config/mcp"
MCP_CONFIG_FILE="${MCP_CONFIG_DIR}/render.json"
TEMPLATE_FILE="${PROJECT_ROOT}/config/mcp/render.json"

load_env() {
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | grep RENDER_API_KEY | xargs)
    fi
}

setup_mcp_config() {
    echo "🔧 Configuring Render MCP..."
    
    load_env

    if [ -z "$RENDER_API_KEY" ]; then
        echo "❌ Error: RENDER_API_KEY not found"
        echo "💡 Add it to the .env file or export: export RENDER_API_KEY=your_api_key"
        exit 1
    fi

    mkdir -p "$MCP_CONFIG_DIR"

    if [ -f "$MCP_CONFIG_FILE" ]; then
        echo "⚠️  Existing configuration: $MCP_CONFIG_FILE"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "✅ Configuration kept"
            exit 0
        fi
    fi

    envsubst < "$TEMPLATE_FILE" > "$MCP_CONFIG_FILE"

    echo "✅ MCP configured: $MCP_CONFIG_FILE"
    echo ""
    echo "Next step:"
    echo "  Restart your AI editor (VS Code/Cursor/etc)"
    echo ""
    echo "Available commands:"
    echo "  make deploy-logs   - View logs of the last deploy"
    echo "  make deploy-status - Service status"
}

setup_mcp_config
