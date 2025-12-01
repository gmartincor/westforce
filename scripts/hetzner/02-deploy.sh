#!/usr/bin/env bash
# =============================================================================
# Deployment script for the Westforce application on Hetzner
# Run as 'deploy' user
# =============================================================================

set -euo pipefail

# === CONFIGURATION ===
APP_DIR="${APP_DIR:-/opt/westforce/app}"
BRANCH="${BRANCH:-hetzner}"
COMPOSE_FILE="docker-compose.prod.yml"
# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# === VERIFICATIONS ===
if [[ ! -f "$APP_DIR/.env" ]]; then
    log_error "The .env file was not found in $APP_DIR"
    log_error "Copy .env.hetzner.example to .env and configure the variables"
    exit 1
fi

cd "$APP_DIR"

# === DEPLOYMENT START ===
log_info "=== Starting Westforce deployment ==="
DEPLOY_START=$(date +%s)

# === STEP 1: Update code ===
log_step "1/6 - Updating code from Git..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# === STEP 2: Create necessary directories ===
log_step "2/6 - Creating directories..."
mkdir -p logs backups config/traefik/dynamic

# === STEP 3: Build image ===
log_step "3/6 - Building Docker image..."
docker compose -f "$COMPOSE_FILE" build --no-cache web

# === STEP 4: Stop previous services (if any) ===
log_step "4/6 - Updating services..."
if docker compose -f "$COMPOSE_FILE" ps -q 2>/dev/null | grep -q .; then
    log_info "Stopping existing services..."
    docker compose -f "$COMPOSE_FILE" down --remove-orphans
fi

# === STEP 5: Start services ===
log_step "5/6 - Starting services..."
docker compose -f "$COMPOSE_FILE" up -d

# === STEP 6: Verify status ===
log_step "6/6 - Verifying service status..."
sleep 10

# Verify that containers are running
SERVICES=("westforce-traefik" "westforce-postgres" "westforce-web")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    STATUS=$(docker inspect -f '{{.State.Status}}' "$service" 2>/dev/null || echo "not found")
    if [[ "$STATUS" == "running" ]]; then
        log_info "✓ $service: $STATUS"
    else
        log_error "✗ $service: $STATUS"
        ALL_HEALTHY=false
    fi
done

# Verify application health check
log_info "Waiting for the application to be ready..."
MAX_RETRIES=30
RETRY=0
while [[ $RETRY -lt $MAX_RETRIES ]]; do
    if curl -sf http://localhost:8000/health/ > /dev/null 2>&1; then
        log_info "✓ Application responding correctly"
        break
    fi
    RETRY=$((RETRY + 1))
    sleep 2
done

if [[ $RETRY -eq $MAX_RETRIES ]]; then
    log_error "The application did not respond after $MAX_RETRIES attempts"
    log_error "Check the logs: docker compose -f $COMPOSE_FILE logs web"
    ALL_HEALTHY=false
fi

# === SUMMARY ===
DEPLOY_END=$(date +%s)
DEPLOY_DURATION=$((DEPLOY_END - DEPLOY_START))

echo ""
echo "=============================================="
if [[ "$ALL_HEALTHY" == true ]]; then
    echo -e "${GREEN}✅ DEPLOYMENT COMPLETED SUCCESSFULLY${NC}"
else
    echo -e "${RED}⚠️  DEPLOYMENT COMPLETED WITH WARNINGS${NC}"
fi
echo "=============================================="
echo "Duration: ${DEPLOY_DURATION}s"
echo "Branch: $BRANCH"
echo "Date: $(date)"
echo ""
echo "Useful commands:"
echo "  - View logs: docker compose -f $COMPOSE_FILE logs -f"
echo "  - View status: docker compose -f $COMPOSE_FILE ps"
echo "  - Restart: docker compose -f $COMPOSE_FILE restart"
echo ""

if [[ "$ALL_HEALTHY" == false ]]; then
    exit 1
fi
