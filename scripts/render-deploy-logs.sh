#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

load_env() {
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | grep RENDER_API_KEY | xargs)
    fi
}

get_service_id() {
    local response=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
        "https://api.render.com/v1/services?name=westforce&limit=1")
    echo "$response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4
}

get_latest_deploy() {
    local service_id=$1
    local response=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
        "https://api.render.com/v1/services/$service_id/deploys?limit=1")
    echo "$response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4
}

show_deploy_logs() {
    echo "🚀 Obteniendo logs del deploy de westforce..."
    echo ""
    
    load_env
    
    if [ -z "$RENDER_API_KEY" ]; then
        echo "❌ Error: RENDER_API_KEY no encontrada"
        echo "💡 Ejecuta: make mcp-setup"
        exit 1
    fi
    
    SERVICE_ID=$(get_service_id)
    
    if [ -z "$SERVICE_ID" ]; then
        echo "❌ Servicio westforce no encontrado"
        exit 1
    fi
    
    DEPLOY_ID=$(get_latest_deploy "$SERVICE_ID")
    
    if [ -z "$DEPLOY_ID" ]; then
        echo "❌ No deploys found"
        exit 1
    fi
    
    echo "📋 Service: $SERVICE_ID"
    echo "📋 Deploy: $DEPLOY_ID"
    echo ""
    
    curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
        "https://api.render.com/v1/services/$SERVICE_ID/deploys/$DEPLOY_ID/logs" | \
        grep -o '"message":"[^"]*' | cut -d'"' -f4 | while IFS= read -r line; do
            echo "$line"
        done
}

show_deploy_logs
