#!/bin/bash

MODE=${1:-manager}
PORT=${2:-8001}

echo "🚀 Starting Westforce Development Server"
echo "Mode: $MODE"
echo "Port: $PORT"
echo ""

if [ "$MODE" = "landing" ]; then
    echo "📄 LANDING PAGE MODE"
    echo "Access: http://localhost:$PORT/"
    echo ""
    DEV_FORCE_LANDING=True docker-compose --env-file .env.dev-with-prod-db run --rm -p $PORT:$PORT web python manage.py runserver 0.0.0.0:$PORT
elif [ "$MODE" = "manager" ]; then
    echo "🎛️  MANAGER PANEL MODE"
    echo "Access: http://localhost:$PORT/"
    echo "Login: westforce / westforce"
    echo ""
    DEV_FORCE_LANDING=False docker-compose --env-file .env.dev-with-prod-db run --rm -p $PORT:$PORT web python manage.py runserver 0.0.0.0:$PORT
else
    echo "❌ Invalid mode. Use: manager or landing"
    echo "Usage: ./dev.sh [manager|landing] [port]"
    exit 1
fi
