#!/bin/bash

set -e

echo "🔧 Westforce - Render MCP Quick Start"
echo ""
echo "1️⃣  Configuring MCP..."

if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    exit 1
fi

export $(grep -v '^#' .env | grep RENDER_API_KEY | xargs)

if [ -z "$RENDER_API_KEY" ]; then
    echo "❌ RENDER_API_KEY not set in .env"
    exit 1
fi

./scripts/setup-mcp.sh

echo ""
echo "2️⃣  Checking service on Render..."
./scripts/render-service-status.sh

echo ""
echo "✅ Setup completed!"
echo ""
echo "📝 Next steps:"
echo "   1. Restart VS Code"
echo "   2. Use prompts like:"
echo "      - 'Show latest deploy logs for westforce-web'"
echo "      - 'What's the status of westforce service?'"
echo "      - 'List recent deploys'"
echo ""
echo "💡 Direct commands:"
echo "   make deploy-logs"
echo "   make deploy-status"
