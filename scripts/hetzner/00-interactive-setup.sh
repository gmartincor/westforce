#!/usr/bin/env bash
# =============================================================================
# Script interactivo para la provisión inicial del servidor Hetzner
# Este script te guía paso a paso por todo el proceso
# =============================================================================

set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     🚀 WESTFORCE - ASISTENTE DE DESPLIEGUE EN HETZNER 🚀     ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# === FASE 0: Verificación de requisitos locales ===
echo -e "${BLUE}═══ FASE 0: Verificación de requisitos locales ═══${NC}"
echo ""

check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $1 instalado"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 no encontrado"
        return 1
    fi
}

MISSING_DEPS=false
check_command "ssh" || MISSING_DEPS=true
check_command "ssh-keygen" || MISSING_DEPS=true
check_command "git" || MISSING_DEPS=true
check_command "curl" || MISSING_DEPS=true

if [[ "$MISSING_DEPS" == true ]]; then
    echo ""
    echo -e "${RED}Error: Faltan dependencias. Instálalas antes de continuar.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Todos los requisitos locales cumplidos${NC}"
echo ""

# === FASE 1: Verificar clave SSH ===
echo -e "${BLUE}═══ FASE 1: Configuración de clave SSH ═══${NC}"
echo ""

SSH_KEY_PATH="$HOME/.ssh/id_ed25519"
SSH_PUB_KEY_PATH="$HOME/.ssh/id_ed25519.pub"

if [[ -f "$SSH_PUB_KEY_PATH" ]]; then
    echo -e "${GREEN}✓${NC} Clave SSH encontrada en $SSH_PUB_KEY_PATH"
    echo ""
    echo "Tu clave pública SSH (necesaria para Hetzner):"
    echo ""
    echo -e "${CYAN}"
    cat "$SSH_PUB_KEY_PATH"
    echo -e "${NC}"
else
    echo -e "${YELLOW}No se encontró una clave SSH ed25519.${NC}"
    read -p "¿Deseas generar una nueva clave SSH? (y/N): " generate_key
    if [[ "$generate_key" =~ ^[Yy]$ ]]; then
        read -p "Email para la clave SSH: " ssh_email
        ssh-keygen -t ed25519 -C "$ssh_email" -f "$SSH_KEY_PATH"
        echo ""
        echo "Tu nueva clave pública SSH:"
        echo ""
        echo -e "${CYAN}"
        cat "$SSH_PUB_KEY_PATH"
        echo -e "${NC}"
    else
        echo -e "${RED}Error: Se necesita una clave SSH para continuar.${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${YELLOW}IMPORTANTE: Copia esta clave y añádela a Hetzner Cloud Console:${NC}"
echo "  1. Ve a https://console.hetzner.cloud"
echo "  2. Proyecto → Security → SSH Keys → Add SSH Key"
echo "  3. Pega tu clave pública"
echo ""
read -p "Presiona Enter cuando hayas añadido la clave a Hetzner..."

# === FASE 2: Crear servidor en Hetzner ===
echo ""
echo -e "${BLUE}═══ FASE 2: Creación del servidor en Hetzner ═══${NC}"
echo ""
echo "Sigue estos pasos en Hetzner Cloud Console:"
echo ""
echo "  1. Ve a https://console.hetzner.cloud"
echo "  2. Crea un nuevo proyecto (ej: 'westforce-production')"
echo "  3. Dentro del proyecto, crea un servidor:"
echo "     - Ubicación: Helsinki (hel1) o Falkenstein (fsn1)"
echo "     - Imagen: Ubuntu 24.04"
echo "     - Tipo: CX23 (2 vCPU, 4GB RAM, 40GB SSD) - €0.0056/hora"
echo "     - SSH Key: Selecciona la clave que añadiste"
echo "     - Backups: Activar (recomendado, +20%)"
echo "     - Nombre: westforce-prod"
echo ""
read -p "Introduce la IP del servidor creado: " SERVER_IP

if [[ -z "$SERVER_IP" ]]; then
    echo -e "${RED}Error: Se necesita la IP del servidor.${NC}"
    exit 1
fi

# Validar formato IP
if ! [[ "$SERVER_IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Error: Formato de IP inválido.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓${NC} Servidor configurado: $SERVER_IP"

# === FASE 3: Probar conexión SSH ===
echo ""
echo -e "${BLUE}═══ FASE 3: Verificación de conexión SSH ═══${NC}"
echo ""
echo "Probando conexión SSH..."

if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@"$SERVER_IP" "echo 'Conexión exitosa'" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Conexión SSH establecida correctamente"
else
    echo -e "${RED}✗${NC} No se pudo conectar al servidor"
    echo ""
    echo "Posibles causas:"
    echo "  - El servidor aún está iniciando (espera 1-2 minutos)"
    echo "  - La clave SSH no está configurada correctamente"
    echo "  - La IP es incorrecta"
    echo ""
    read -p "¿Reintentar? (y/N): " retry
    if [[ "$retry" =~ ^[Yy]$ ]]; then
        exec "$0"
    fi
    exit 1
fi

# === FASE 4: Preparar servidor ===
echo ""
echo -e "${BLUE}═══ FASE 4: Preparación del servidor ═══${NC}"
echo ""
echo "Se va a ejecutar el script de hardening del servidor."
echo "Esto instalará:"
echo "  - Docker y Docker Compose"
echo "  - Firewall (UFW)"
echo "  - Fail2ban"
echo "  - Usuario 'deploy'"
echo "  - Swap de 2GB"
echo ""
read -p "¿Continuar con la preparación del servidor? (y/N): " prepare_server

if [[ "$prepare_server" =~ ^[Yy]$ ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "Ejecutando script de preparación..."
    ssh root@"$SERVER_IP" 'bash -s' < "$SCRIPT_DIR/01-server-setup.sh"
    echo ""
    echo -e "${GREEN}✓${NC} Servidor preparado correctamente"
fi

# === FASE 5: Clonar repositorio ===
echo ""
echo -e "${BLUE}═══ FASE 5: Despliegue de la aplicación ═══${NC}"
echo ""

read -p "¿Deseas clonar el repositorio y desplegar ahora? (y/N): " deploy_now

if [[ "$deploy_now" =~ ^[Yy]$ ]]; then
    echo "Clonando repositorio y configurando..."
    ssh deploy@"$SERVER_IP" << 'REMOTE_SCRIPT'
        set -e
        
        # Clonar repositorio
        if [[ ! -d /opt/westforce/app ]]; then
            sudo mkdir -p /opt/westforce
            sudo chown deploy:deploy /opt/westforce
            git clone https://github.com/gmartincor/westforce.git /opt/westforce/app
        fi
        
        cd /opt/westforce/app
        git checkout hetzner
        git pull origin hetzner
        
        # Crear directorios necesarios
        mkdir -p logs backups config/traefik/dynamic
        
        echo ""
        echo "Repositorio clonado en /opt/westforce/app"
        echo "Ahora necesitas:"
        echo "  1. Copiar .env.hetzner.example a .env"
        echo "  2. Editar .env con tus valores reales"
        echo "  3. Ejecutar: docker compose -f docker-compose.prod.yml up -d"
REMOTE_SCRIPT

    echo ""
    echo -e "${YELLOW}IMPORTANTE: Antes de iniciar la aplicación, configura las variables de entorno:${NC}"
    echo ""
    echo "  ssh deploy@$SERVER_IP"
    echo "  cd /opt/westforce/app"
    echo "  cp .env.hetzner.example .env"
    echo "  nano .env  # Edita con tus valores"
    echo "  docker compose -f docker-compose.prod.yml up -d"
fi

# === RESUMEN FINAL ===
echo ""
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              🎉 CONFIGURACIÓN COMPLETADA 🎉                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "📋 RESUMEN:"
echo "  - Servidor: $SERVER_IP"
echo "  - Usuario de despliegue: deploy"
echo "  - Directorio de la app: /opt/westforce/app"
echo ""
echo "📝 PRÓXIMOS PASOS:"
echo "  1. Configurar DNS apuntando westforceremovals.com a $SERVER_IP"
echo "  2. Crear cuenta en https://healthchecks.io"
echo "  3. Configurar variables de entorno en .env"
echo "  4. Iniciar la aplicación con Docker Compose"
echo "  5. Configurar los secrets de GitHub Actions"
echo ""
echo "🔗 COMANDOS ÚTILES:"
echo "  - Conectar al servidor: ssh deploy@$SERVER_IP"
echo "  - Ver logs: docker compose -f docker-compose.prod.yml logs -f"
echo "  - Reiniciar: docker compose -f docker-compose.prod.yml restart"
echo ""
echo "📚 Documentación completa: docs/HETZNER_DEPLOYMENT_PLAN.md"
echo ""
