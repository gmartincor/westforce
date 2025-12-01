#!/usr/bin/env bash
# =============================================================================
# Script de preparación del servidor Hetzner para Westforce
# Ejecutar como root en un servidor Ubuntu 24.04 LTS recién creado
# Optimizado para Hetzner CX23 (2 vCPU, 4GB RAM, 40GB SSD)
# =============================================================================

set -euo pipefail

# === CONFIGURACIÓN ===
DEPLOY_USER="${DEPLOY_USER:-deploy}"
SSH_PORT="${SSH_PORT:-22}"
SWAP_SIZE="${SWAP_SIZE:-2G}"
TIMEZONE="${TIMEZONE:-Australia/Perth}"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# === VERIFICACIONES INICIALES ===
if [[ $EUID -ne 0 ]]; then
    log_error "Este script debe ejecutarse como root"
    exit 1
fi

log_info "=== Iniciando preparación del servidor Hetzner ==="
log_info "Usuario de despliegue: $DEPLOY_USER"
log_info "Puerto SSH: $SSH_PORT"
log_info "Tamaño swap: $SWAP_SIZE"

# === ACTUALIZACIÓN DEL SISTEMA ===
log_info "Actualizando sistema..."
apt update -y
DEBIAN_FRONTEND=noninteractive apt upgrade -y

# === CONFIGURACIÓN DE TIMEZONE ===
log_info "Configurando timezone a $TIMEZONE..."
timedatectl set-timezone "$TIMEZONE"

# === INSTALACIÓN DE PAQUETES BASE ===
log_info "Instalando paquetes base..."
apt install -y \
    curl \
    git \
    ufw \
    fail2ban \
    build-essential \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    gnupg \
    lsb-release \
    htop \
    ncdu \
    unzip \
    jq \
    vim \
    nano

# === CREACIÓN DEL USUARIO DE DESPLIEGUE ===
log_info "Creando usuario de despliegue '$DEPLOY_USER'..."
if id "$DEPLOY_USER" &>/dev/null; then
    log_warn "El usuario '$DEPLOY_USER' ya existe"
else
    adduser --disabled-password --gecos "" "$DEPLOY_USER"
fi

# Añadir a sudoers sin password para comandos específicos
cat > /etc/sudoers.d/$DEPLOY_USER << EOF
# Permitir al usuario deploy ejecutar comandos docker y systemctl sin password
$DEPLOY_USER ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/docker-compose, /usr/bin/systemctl restart westforce*, /usr/bin/systemctl status westforce*, /usr/local/bin/*-healthcheck.sh, /usr/local/bin/*-monitor.sh
EOF
chmod 440 /etc/sudoers.d/$DEPLOY_USER

# === CONFIGURACIÓN DE SSH ===
log_info "Configurando SSH..."
mkdir -p /home/$DEPLOY_USER/.ssh
if [[ -f ~/.ssh/authorized_keys ]]; then
    cp ~/.ssh/authorized_keys /home/$DEPLOY_USER/.ssh/authorized_keys
else
    log_warn "No se encontró ~/.ssh/authorized_keys, deberás añadir tu clave SSH manualmente"
    touch /home/$DEPLOY_USER/.ssh/authorized_keys
fi
chmod 700 /home/$DEPLOY_USER/.ssh
chmod 600 /home/$DEPLOY_USER/.ssh/authorized_keys
chown -R $DEPLOY_USER:$DEPLOY_USER /home/$DEPLOY_USER/.ssh

# Reforzar configuración SSH
cat > /etc/ssh/sshd_config.d/99-hardening.conf << EOF
# Hardening SSH para Westforce
Port ${SSH_PORT}
PermitRootLogin prohibit-password
PasswordAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
X11Forwarding no
AllowTcpForwarding no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers root $DEPLOY_USER
EOF

systemctl restart sshd

# === CONFIGURACIÓN DEL FIREWALL ===
log_info "Configurando firewall UFW..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ${SSH_PORT}/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable

log_info "Reglas de firewall actuales:"
ufw status verbose

# === CONFIGURACIÓN DE SWAP ===
log_info "Configurando swap de $SWAP_SIZE..."
if [[ -f /swapfile ]]; then
    log_warn "Swap ya existe, omitiendo..."
else
    fallocate -l $SWAP_SIZE /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    
    # Optimizar configuración de swap
    cat >> /etc/sysctl.conf << EOF

# Optimización de swap para servidor web
vm.swappiness=10
vm.vfs_cache_pressure=50
EOF
    sysctl -p
fi

# === INSTALACIÓN DE DOCKER ===
log_info "Instalando Docker..."
if command -v docker &> /dev/null; then
    log_warn "Docker ya está instalado"
else
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
fi

# Añadir usuario al grupo docker
usermod -aG docker $DEPLOY_USER

# === INSTALACIÓN DE DOCKER COMPOSE PLUGIN ===
log_info "Verificando Docker Compose..."
if docker compose version &> /dev/null; then
    log_info "Docker Compose ya está instalado: $(docker compose version)"
else
    log_info "Instalando Docker Compose plugin..."
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
        -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

# === CONFIGURACIÓN DE FAIL2BAN ===
log_info "Configurando Fail2Ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ${SSH_PORT}
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 24h
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# === CREACIÓN DE DIRECTORIOS PARA LA APLICACIÓN ===
log_info "Creando estructura de directorios..."
mkdir -p /opt/westforce/{logs,backups,scripts}
chown -R $DEPLOY_USER:$DEPLOY_USER /opt/westforce

# === CONFIGURACIÓN DE LOGROTATE PARA DOCKER ===
log_info "Configurando logrotate para Docker..."
cat > /etc/logrotate.d/docker-containers << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
    size 100M
}
EOF

# === CONFIGURACIÓN DE LÍMITES DEL SISTEMA ===
log_info "Configurando límites del sistema..."
cat >> /etc/security/limits.conf << EOF

# Límites para Westforce
$DEPLOY_USER soft nofile 65535
$DEPLOY_USER hard nofile 65535
$DEPLOY_USER soft nproc 4096
$DEPLOY_USER hard nproc 4096
EOF

# === CONFIGURACIÓN DE KERNEL ===
log_info "Optimizando parámetros del kernel..."
cat >> /etc/sysctl.conf << EOF

# Optimización de red para servidor web
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=65535
net.ipv4.ip_local_port_range=1024 65535
net.ipv4.tcp_tw_reuse=1
net.ipv4.tcp_fin_timeout=15
net.core.netdev_max_backlog=65535
EOF
sysctl -p 2>/dev/null || true

# === LIMPIEZA ===
log_info "Limpiando paquetes innecesarios..."
apt autoremove -y
apt clean

# === RESUMEN FINAL ===
echo ""
echo "=============================================="
echo -e "${GREEN}✅ SERVIDOR PREPARADO EXITOSAMENTE${NC}"
echo "=============================================="
echo ""
echo "Información del servidor:"
echo "  - Usuario de despliegue: $DEPLOY_USER"
echo "  - Puerto SSH: $SSH_PORT"
echo "  - Swap: $SWAP_SIZE"
echo "  - Timezone: $TIMEZONE"
echo "  - Docker: $(docker --version)"
echo "  - Docker Compose: $(docker compose version)"
echo ""
echo "Próximos pasos:"
echo "  1. Cierra esta sesión SSH"
echo "  2. Conéctate como el usuario deploy:"
echo "     ssh -p ${SSH_PORT} ${DEPLOY_USER}@$(hostname -I | awk '{print $1}')"
echo "  3. Clona el repositorio y despliega:"
echo "     git clone https://github.com/gmartincor/westforce.git /opt/westforce/app"
echo "     cd /opt/westforce/app && git checkout hetzner"
echo ""
echo "⚠️  IMPORTANTE: Guarda la IP y el puerto SSH para futuras conexiones"
echo ""
