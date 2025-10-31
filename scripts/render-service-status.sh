#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

load_env() {
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | grep RENDER_API_KEY | xargs)
    fi
}

get_service_status() {
    echo "📊 Estado del servicio westforce..."
    echo ""
    
    load_env
    
    if [ -z "$RENDER_API_KEY" ]; then
        echo "❌ Error: RENDER_API_KEY no encontrada"
        exit 1
    fi
    
    local response=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
        "https://api.render.com/v1/services?name=westforce&limit=1")
    
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data and len(data) > 0:
        service = data[0]['service']
        print(f\"🆔 ID: {service['id']}\")
        print(f\"📛 Name: {service['name']}\")
        print(f\"🌐 Type: {service['type']}\")
        print(f\"📍 Region: {service['region']}\")
        print(f\"🔄 Status: {service.get('serviceDetails', {}).get('status', 'unknown')}\")
        print(f\"🌿 Branch: {service.get('branch', 'unknown')}\")
        print(f\"🔗 URL: {service.get('serviceDetails', {}).get('url', 'N/A')}\")
    else:
        print('❌ Service not found')
except:
    print('❌ Error processing response')
"
}

get_service_status
