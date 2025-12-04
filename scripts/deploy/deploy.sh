#!/usr/bin/env bash
# =============================================================================
# Script de Despliegue para Westforce
# Ejecutar como usuario 'deploy'
# =============================================================================

set -euo pipefail

# === CONFIGURACIÓN ===
APP_DIR="${APP_DIR:-/opt/projects/westforce}"
BRANCH="${BRANCH:-main}"
COMPOSE_FILE="docker-compose.prod.yml"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# === VERIFICACIONES ===
if [[ ! -f "$APP_DIR/.env" ]]; then
    log_error "El archivo .env no se encuentra en $APP_DIR"
    log_error "Copia .env.production.example a .env y configura las variables"
    exit 1
fi

cd "$APP_DIR"

# === INICIO DEL DESPLIEGUE ===
log_info "=== Iniciando despliegue de Westforce ==="
DEPLOY_START=$(date +%s)

# === PASO 1: Actualizar código ===
log_step "1/6 - Actualizando código desde Git..."
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# === PASO 2: Crear directorios necesarios ===
log_step "2/6 - Creando directorios..."
mkdir -p logs backups

# === PASO 3: Verificar red de Traefik ===
log_step "3/6 - Verificando red traefik-public..."
if ! docker network ls | grep -q "traefik-public"; then
    log_warn "Red traefik-public no existe. Creándola..."
    docker network create traefik-public
fi

# === PASO 4: Construir imagen ===
log_step "4/6 - Construyendo imagen Docker..."
docker compose -f "$COMPOSE_FILE" build web

# === PASO 5: Actualizar servicios ===
log_step "5/6 - Actualizando servicios..."
if docker compose -f "$COMPOSE_FILE" ps -q 2>/dev/null | grep -q .; then
    log_info "Deteniendo servicios existentes..."
    docker compose -f "$COMPOSE_FILE" down --remove-orphans
fi

log_info "Iniciando servicios..."
docker compose -f "$COMPOSE_FILE" up -d

# === PASO 6: Verificar estado ===
log_step "6/6 - Verificando estado de los servicios..."
sleep 10

# Verificar que los contenedores están corriendo
SERVICES=("westforce-postgres" "westforce-web")
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

# Verificar health check de la aplicación
log_info "Esperando a que la aplicación esté lista..."
MAX_RETRIES=30
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
    log_error "La aplicación no respondió después de $MAX_RETRIES intentos"
    log_error "Revisa los logs: docker compose -f $COMPOSE_FILE logs web"
    ALL_HEALTHY=false
fi

# === RESUMEN ===
DEPLOY_END=$(date +%s)
DEPLOY_DURATION=$((DEPLOY_END - DEPLOY_START))

echo ""
echo "=============================================="
if [[ "$ALL_HEALTHY" == true ]]; then
    echo -e "${GREEN}✅ DESPLIEGUE COMPLETADO EXITOSAMENTE${NC}"
else
    echo -e "${RED}⚠️  DESPLIEGUE COMPLETADO CON ADVERTENCIAS${NC}"
fi
echo "=============================================="
echo "Duración: ${DEPLOY_DURATION}s"
echo "Branch: $BRANCH"
echo "Fecha: $(date)"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: docker compose -f $COMPOSE_FILE logs -f"
echo "  - Ver estado: docker compose -f $COMPOSE_FILE ps"
echo "  - Reiniciar: docker compose -f $COMPOSE_FILE restart"
echo ""

if [[ "$ALL_HEALTHY" == false ]]; then
    exit 1
fi
