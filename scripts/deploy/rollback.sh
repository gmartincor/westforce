#!/usr/bin/env bash
# =============================================================================
# Script de Rollback para Westforce
# Revierte al commit anterior si hay problemas con el despliegue
# =============================================================================

set -euo pipefail

APP_DIR="${APP_DIR:-/opt/projects/westforce}"
COMPOSE_FILE="docker-compose.prod.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cd "$APP_DIR"

# Obtener información del commit actual
CURRENT_COMMIT=$(git rev-parse HEAD)
CURRENT_COMMIT_SHORT=$(git rev-parse --short HEAD)
CURRENT_COMMIT_MSG=$(git log -1 --pretty=%B)

log_info "Commit actual: $CURRENT_COMMIT_SHORT"
log_info "Mensaje: $CURRENT_COMMIT_MSG"

# Obtener commit anterior
PREVIOUS_COMMIT=$(git rev-parse HEAD~1)
PREVIOUS_COMMIT_SHORT=$(git rev-parse --short HEAD~1)
PREVIOUS_COMMIT_MSG=$(git log -1 --pretty=%B HEAD~1)

echo ""
log_warn "⚠️  Este script revertirá al commit anterior:"
log_warn "   $PREVIOUS_COMMIT_SHORT - $PREVIOUS_COMMIT_MSG"
echo ""
read -p "¿Continuar con el rollback? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Rollback cancelado"
    exit 0
fi

log_info "Iniciando rollback..."

# Guardar el commit actual por si necesitamos volver
git stash push -m "Stash before rollback to $PREVIOUS_COMMIT_SHORT" 2>/dev/null || true

# Revertir al commit anterior
log_info "Revirtiendo a $PREVIOUS_COMMIT_SHORT..."
git checkout "$PREVIOUS_COMMIT"

# Reconstruir y redesplegar
log_info "Reconstruyendo imagen..."
docker compose -f "$COMPOSE_FILE" build web

log_info "Redesplegando servicios..."
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

# Esperar y verificar
log_info "Esperando a que la aplicación esté lista..."
sleep 15

MAX_RETRIES=20
RETRY=0
while [[ $RETRY -lt $MAX_RETRIES ]]; do
    if curl -sf http://localhost:8000/health/ > /dev/null 2>&1; then
        log_info "✓ Aplicación respondiendo correctamente"
        break
    fi
    RETRY=$((RETRY + 1))
    sleep 2
done

if [[ $RETRY -eq $MAX_RETRIES ]]; then
    log_error "La aplicación no respondió después del rollback"
    log_error "Revisa los logs: docker compose -f $COMPOSE_FILE logs web"
    exit 1
fi

echo ""
echo "=============================================="
echo -e "${GREEN}✅ ROLLBACK COMPLETADO${NC}"
echo "=============================================="
echo "Revertido de: $CURRENT_COMMIT_SHORT"
echo "A: $PREVIOUS_COMMIT_SHORT"
echo ""
echo "Para volver al commit anterior (deshacer rollback):"
echo "  git checkout $CURRENT_COMMIT_SHORT"
echo "  ./scripts/deploy/deploy.sh"
echo ""
