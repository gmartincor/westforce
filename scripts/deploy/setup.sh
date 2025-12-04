#!/usr/bin/env bash
# =============================================================================
# Setup inicial para Westforce en Hostinger VPS
# Ejecutar en el servidor como usuario deploy
# =============================================================================

set -euo pipefail

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

# === CONFIGURACIÓN ===
APP_DIR="${APP_DIR:-/opt/projects/westforce}"
INFRA_DIR="${INFRA_DIR:-/opt/infrastructure}"
DOMAIN="westforceremovals.com"

echo "=============================================="
echo "  Westforce - Setup Hostinger VPS"
echo "  Dominio: $DOMAIN"
echo "=============================================="
echo ""

# === VERIFICACIONES ===
log_step "Verificando pre-requisitos..."

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado. Ejecuta primero el setup de infrastructure:"
    log_error "  cd /opt/infrastructure && sudo ./scripts/setup-inicial.sh"
    exit 1
fi

# Verificar red traefik-public
if ! docker network ls | grep -q "traefik-public"; then
    log_warn "Red traefik-public no existe. Creándola..."
    docker network create traefik-public
fi

# Verificar Traefik
if ! docker ps | grep -q "traefik"; then
    log_warn "Traefik no está corriendo. Asegúrate de iniciarlo:"
    log_warn "  cd $INFRA_DIR/traefik && docker compose up -d"
fi

log_info "Pre-requisitos OK"

# === CREAR DIRECTORIOS ===
log_step "Creando estructura de directorios..."
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/backups"

# === CLONAR O ACTUALIZAR REPO ===
log_step "Preparando repositorio..."
if [[ -d "$APP_DIR/.git" ]]; then
    log_info "Repositorio ya existe, actualizando..."
    cd "$APP_DIR"
    git fetch origin
    git checkout main
    git pull origin main
else
    log_info "Clonando repositorio..."
    git clone https://github.com/gmartincor/westforce.git "$APP_DIR"
    cd "$APP_DIR"
fi

# === VERIFICAR ARCHIVO .env ===
if [[ ! -f "$APP_DIR/.env" ]]; then
    log_warn "Archivo .env no encontrado"
    log_info "Copiando ejemplo de configuración..."
    cp "$APP_DIR/.env.hostinger.example" "$APP_DIR/.env"
    
    # Generar SECRET_KEY automáticamente
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s|<GENERA_UNA_CLAVE_SEGURA>|$SECRET_KEY|g" "$APP_DIR/.env"
    
    # Generar DB_PASSWORD automáticamente
    DB_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
    sed -i "s|<GENERA_UN_PASSWORD_SEGURO>|$DB_PASSWORD|g" "$APP_DIR/.env"
    
    log_info "✓ SECRET_KEY generada"
    log_info "✓ DB_PASSWORD generada"
    echo ""
    log_warn "IMPORTANTE: Revisa y ajusta el archivo .env antes de desplegar:"
    log_warn "  nano $APP_DIR/.env"
    echo ""
fi

log_info "Setup completado!"
echo ""
echo "=============================================="
echo "  Próximos pasos:"
echo "=============================================="
echo ""
echo "1. Verifica la configuración:"
echo "   nano $APP_DIR/.env"
echo ""
echo "2. Despliega la aplicación:"
echo "   cd $APP_DIR && ./scripts/deploy/deploy.sh"
echo ""
echo "3. Verifica el estado:"
echo "   docker compose -f docker-compose.prod.yml ps"
echo ""
