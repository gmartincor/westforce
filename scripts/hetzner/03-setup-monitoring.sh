#!/usr/bin/env bash
# =============================================================================
# Monitoring configuration script for Westforce
# Configures healthchecks.io for heartbeat, resource monitoring, and auto-recovery
# Run as root or with sudo
# 
# ZERO-MAINTENANCE FEATURES:
# - Automatic container restarts via Docker
# - Health check pings to healthchecks.io
# - Resource monitoring with alerts
# - Auto-recovery of hung containers
# - Docker daemon watchdog
# - Disk space alerts
# - Automatic cleanup
# =============================================================================

set -euo pipefail

# === CONFIGURATION ===
SCRIPTS_DIR="/usr/local/bin"
APP_DIR="${APP_DIR:-/opt/westforce/app}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# === VERIFY SCRIPT IS RUN AS ROOT ===
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root or with sudo"
    exit 1
fi

# === LOAD ENVIRONMENT VARIABLES ===
if [[ -f "$APP_DIR/.env" ]]; then
    set -a
    source "$APP_DIR/.env"
    set +a
else
    log_warn "The .env file was not found in $APP_DIR"
    log_warn "Using default/provided Healthchecks.io URL"
fi

# Default URL from user's healthchecks.io account (guillermomc007@gmail.com)
HEALTHCHECK_HEARTBEAT_URL="${HEALTHCHECK_HEARTBEAT_URL:-https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c}"
HEALTHCHECK_FAILURE_URL="${HEALTHCHECK_FAILURE_URL:-https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c/fail}"

log_info "=== Configuring Westforce ZERO-MAINTENANCE Monitoring ==="
log_info "Healthchecks.io URL: ${HEALTHCHECK_HEARTBEAT_URL}"

# === CREATE HEARTBEAT SCRIPT (WITH AUTO-RECOVERY) ===
log_step "1/7 - Creating heartbeat script with auto-recovery..."
cat > "$SCRIPTS_DIR/westforce-healthcheck.sh" << 'HEALTHSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

# Load configuration
APP_DIR="/opt/westforce/app"
if [[ -f "$APP_DIR/.env" ]]; then
    set -a
    source "$APP_DIR/.env"
    set +a
fi

HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health/}"
SUCCESS_PING="${HEALTHCHECK_HEARTBEAT_URL:-https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c}"
FAILURE_PING="${HEALTHCHECK_FAILURE_URL:-https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c/fail}"
LOG_FILE="/var/log/westforce-healthcheck.log"
MAX_FAILURES=3
FAILURE_COUNT_FILE="/tmp/westforce_health_failures"

# Initialize failure counter
if [[ ! -f "$FAILURE_COUNT_FILE" ]]; then
    echo "0" > "$FAILURE_COUNT_FILE"
fi

# Check if the health endpoint responds correctly
if curl --silent --max-time 10 --fail "$HEALTH_URL" >/dev/null 2>&1; then
    # Application is healthy - send success ping
    curl --silent --max-time 5 "$SUCCESS_PING" >/dev/null 2>&1 || true
    # Reset failure counter
    echo "0" > "$FAILURE_COUNT_FILE"
else
    # Application is not responding - increment failure counter
    FAILURES=$(cat "$FAILURE_COUNT_FILE")
    FAILURES=$((FAILURES + 1))
    echo "$FAILURES" > "$FAILURE_COUNT_FILE"
    
    echo "$(date): Health check failed ($FAILURES consecutive failures)" >> "$LOG_FILE"
    
    # AUTO-RECOVERY: After MAX_FAILURES consecutive failures, restart the container
    if [[ $FAILURES -ge $MAX_FAILURES ]]; then
        echo "$(date): AUTO-RECOVERY - Restarting westforce-web after $MAX_FAILURES failures..." >> "$LOG_FILE"
        
        # Try to restart the web container
        cd "$APP_DIR"
        docker compose -f docker-compose.prod.yml restart web >> "$LOG_FILE" 2>&1 || true
        
        # Send failure ping with recovery message
        curl --silent --max-time 5 --data-raw "AUTO-RECOVERY: Restarted after $MAX_FAILURES failures" "$FAILURE_PING" >/dev/null 2>&1 || true
        
        # Reset counter after recovery attempt
        echo "0" > "$FAILURE_COUNT_FILE"
    else
        # Just send failure ping
        curl --silent --max-time 5 --data-raw "Health check failed ($FAILURES/$MAX_FAILURES)" "$FAILURE_PING" >/dev/null 2>&1 || true
    fi
fi
HEALTHSCRIPT

chmod 755 "$SCRIPTS_DIR/westforce-healthcheck.sh"
log_info "✓ Heartbeat script with auto-recovery created"

# === CREATE RESOURCE MONITORING SCRIPT (WITH SCALING ALERTS) ===
log_step "2/7 - Creating resource monitoring script with scaling alerts..."
cat > "$SCRIPTS_DIR/westforce-resource-monitor.sh" << 'RESOURCESCRIPT'
#!/usr/bin/env bash
set -euo pipefail

# Load configuration
APP_DIR="/opt/westforce/app"
if [[ -f "$APP_DIR/.env" ]]; then
    set -a
    source "$APP_DIR/.env"
    set +a
fi

# Configurable thresholds (default: alert if exceeding 90%)
CPU_THRESHOLD="${CPU_THRESHOLD:-90}"
RAM_THRESHOLD="${RAM_THRESHOLD:-90}"
DISK_THRESHOLD="${DISK_THRESHOLD:-85}"

# Warning thresholds (lower) - for "consider scaling" alerts
CPU_WARNING="${CPU_WARNING:-75}"
RAM_WARNING="${RAM_WARNING:-80}"
DISK_WARNING="${DISK_WARNING:-70}"

FAILURE_PING="${HEALTHCHECK_FAILURE_URL:-https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c/fail}"
LOG_FILE="/var/log/westforce-resources.log"

# Get CPU usage (1-second average)
cpu_usage=$(top -bn2 -d1 | grep "Cpu(s)" | tail -1 | awk '{print int(100 - $8)}')

# Get RAM usage
ram_usage=$(free | awk '/Mem:/ {printf("%.0f", $3/$2*100)}')

# Get disk usage for root partition
disk_usage=$(df / | awk 'NR==2 {print int($5)}')

# Get disk usage for /opt/westforce (if mounted separately)
westforce_disk=$(df /opt/westforce 2>/dev/null | awk 'NR==2 {print int($5)}' || echo "$disk_usage")

# Get Docker disk usage
docker_disk=$(docker system df --format '{{.Size}}' 2>/dev/null | head -1 || echo "N/A")

# Prepare alert messages
alert_needed=false
warning_needed=false
critical_msg=""
warning_msg=""

# CRITICAL ALERTS (immediate action needed)
if (( cpu_usage >= CPU_THRESHOLD )); then
    alert_needed=true
    critical_msg+="🔴 CPU CRITICAL: ${cpu_usage}% | "
fi

if (( ram_usage >= RAM_THRESHOLD )); then
    alert_needed=true
    critical_msg+="🔴 RAM CRITICAL: ${ram_usage}% | "
fi

if (( disk_usage >= DISK_THRESHOLD )); then
    alert_needed=true
    critical_msg+="🔴 DISK CRITICAL: ${disk_usage}% | "
fi

# WARNING ALERTS (consider scaling)
if (( cpu_usage >= CPU_WARNING && cpu_usage < CPU_THRESHOLD )); then
    warning_needed=true
    warning_msg+="🟡 CPU HIGH: ${cpu_usage}% (Consider upgrading to CX32) | "
fi

if (( ram_usage >= RAM_WARNING && ram_usage < RAM_THRESHOLD )); then
    warning_needed=true
    warning_msg+="🟡 RAM HIGH: ${ram_usage}% (Consider upgrading to CX32) | "
fi

if (( disk_usage >= DISK_WARNING && disk_usage < DISK_THRESHOLD )); then
    warning_needed=true
    warning_msg+="🟡 DISK HIGH: ${disk_usage}% (Consider expanding storage) | "
fi

# Send alerts
if [[ "$alert_needed" == true ]]; then
    curl --silent --max-time 5 --data-raw "CRITICAL: $critical_msg" "$FAILURE_PING" >/dev/null 2>&1 || true
    echo "$(date): CRITICAL - $critical_msg" >> "$LOG_FILE"
elif [[ "$warning_needed" == true ]]; then
    # Send warning (not as failure, but as a note)
    curl --silent --max-time 5 --data-raw "WARNING: $warning_msg" "$FAILURE_PING" >/dev/null 2>&1 || true
    echo "$(date): WARNING - $warning_msg" >> "$LOG_FILE"
fi

# Log current stats periodically (every hour, based on minute = 00)
current_minute=$(date +%M)
if [[ "$current_minute" == "00" ]]; then
    echo "$(date): Stats - CPU:${cpu_usage}% RAM:${ram_usage}% DISK:${disk_usage}% Docker:${docker_disk}" >> "$LOG_FILE"
fi
RESOURCESCRIPT

chmod 755 "$SCRIPTS_DIR/westforce-resource-monitor.sh"
log_info "✓ Resource monitoring script with scaling alerts created"

# === CREATE AUTOMATIC BACKUP SCRIPT ===
log_step "3/7 - Creating backup script..."
cat > "$SCRIPTS_DIR/westforce-backup.sh" << 'BACKUPSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/opt/westforce/backups"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/westforce-backup.log"

# Load configuration
APP_DIR="/opt/westforce/app"
if [[ -f "$APP_DIR/.env" ]]; then
    set -a
    source "$APP_DIR/.env"
    set +a
fi

SUCCESS_PING="${HEALTHCHECK_HEARTBEAT_URL:-https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c}"
FAILURE_PING="${HEALTHCHECK_FAILURE_URL:-https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c/fail}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "$(date): Starting database backup..." >> "$LOG_FILE"

# Perform database backup
if docker exec westforce-postgres pg_dump -U "${DB_USER:-westforce}" "${DB_NAME:-westforce_removals}" -Fc > "$BACKUP_DIR/db_$DATE.dump" 2>> "$LOG_FILE"; then
    # Compress backup
    gzip "$BACKUP_DIR/db_$DATE.dump"
    BACKUP_SIZE=$(ls -lh "$BACKUP_DIR/db_$DATE.dump.gz" | awk '{print $5}')
    echo "$(date): Database backup completed successfully ($BACKUP_SIZE)" >> "$LOG_FILE"
else
    echo "$(date): Database backup FAILED" >> "$LOG_FILE"
    curl --silent --max-time 5 --data-raw "BACKUP FAILED: Database dump error" "$FAILURE_PING" >/dev/null 2>&1 || true
    exit 1
fi

# Backup media files (if they exist)
if docker volume ls | grep -q westforce_prod_media_data; then
    echo "$(date): Backing up media files..." >> "$LOG_FILE"
    docker run --rm -v westforce_prod_media_data:/data -v "$BACKUP_DIR":/backup alpine \
        tar czf "/backup/media_$DATE.tar.gz" -C /data . 2>> "$LOG_FILE" || true
fi

# Delete old backups
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "$(date): Backup cleanup completed (keeping last $RETENTION_DAYS days)" >> "$LOG_FILE"

# Send success ping (for backup-specific check if configured)
curl --silent --max-time 5 "$SUCCESS_PING/backup" >/dev/null 2>&1 || true

echo "$(date): === Backup completed ===" >> "$LOG_FILE"
ls -lh "$BACKUP_DIR" | tail -5 >> "$LOG_FILE"
BACKUPSCRIPT

chmod 755 "$SCRIPTS_DIR/westforce-backup.sh"
log_info "✓ Backup script created"

# === CREATE DOCKER WATCHDOG SCRIPT ===
log_step "4/7 - Creating Docker watchdog script..."
cat > "$SCRIPTS_DIR/westforce-docker-watchdog.sh" << 'WATCHDOGSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

# Docker Watchdog - Monitors Docker daemon and restarts if needed
# Also monitors critical containers and restarts them if not running

LOG_FILE="/var/log/westforce-docker-watchdog.log"
APP_DIR="/opt/westforce/app"

# Load configuration
if [[ -f "$APP_DIR/.env" ]]; then
    set -a
    source "$APP_DIR/.env"
    set +a
fi

FAILURE_PING="${HEALTHCHECK_FAILURE_URL:-https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c/fail}"

# Critical containers that must be running
CRITICAL_CONTAINERS=("westforce-web" "westforce-postgres" "westforce-traefik")

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo "$(date): Docker daemon is NOT running! Attempting restart..." >> "$LOG_FILE"
    systemctl restart docker
    sleep 10
    
    if docker info >/dev/null 2>&1; then
        echo "$(date): Docker daemon successfully restarted" >> "$LOG_FILE"
        curl --silent --max-time 5 --data-raw "RECOVERED: Docker daemon was restarted" "$FAILURE_PING" >/dev/null 2>&1 || true
    else
        echo "$(date): CRITICAL - Docker daemon failed to restart!" >> "$LOG_FILE"
        curl --silent --max-time 5 --data-raw "CRITICAL: Docker daemon failed to restart!" "$FAILURE_PING" >/dev/null 2>&1 || true
        exit 1
    fi
fi

# Check each critical container
for container in "${CRITICAL_CONTAINERS[@]}"; do
    STATUS=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
    
    if [[ "$STATUS" != "running" ]]; then
        echo "$(date): Container $container is NOT running (status: $STATUS). Attempting restart..." >> "$LOG_FILE"
        
        cd "$APP_DIR"
        docker compose -f docker-compose.prod.yml up -d "$container" 2>> "$LOG_FILE" || true
        
        sleep 10
        
        NEW_STATUS=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
        if [[ "$NEW_STATUS" == "running" ]]; then
            echo "$(date): Container $container successfully restarted" >> "$LOG_FILE"
            curl --silent --max-time 5 --data-raw "RECOVERED: $container was restarted" "$FAILURE_PING" >/dev/null 2>&1 || true
        else
            echo "$(date): CRITICAL - Failed to restart $container!" >> "$LOG_FILE"
            curl --silent --max-time 5 --data-raw "CRITICAL: Failed to restart $container!" "$FAILURE_PING" >/dev/null 2>&1 || true
        fi
    fi
done
WATCHDOGSCRIPT

chmod 755 "$SCRIPTS_DIR/westforce-docker-watchdog.sh"
log_info "✓ Docker watchdog script created"

# === CREATE DISK CLEANUP SCRIPT ===
log_step "5/7 - Creating automatic disk cleanup script..."
cat > "$SCRIPTS_DIR/westforce-disk-cleanup.sh" << 'CLEANUPSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

# Automatic disk cleanup when disk usage is high
LOG_FILE="/var/log/westforce-cleanup.log"
DISK_THRESHOLD="${DISK_CLEANUP_THRESHOLD:-80}"

disk_usage=$(df / | awk 'NR==2 {print int($5)}')

echo "$(date): Disk usage check: ${disk_usage}%" >> "$LOG_FILE"

if (( disk_usage >= DISK_THRESHOLD )); then
    echo "$(date): Disk usage above ${DISK_THRESHOLD}%, starting cleanup..." >> "$LOG_FILE"
    
    # Clean Docker build cache
    echo "$(date): Cleaning Docker build cache..." >> "$LOG_FILE"
    docker builder prune -f >> "$LOG_FILE" 2>&1 || true
    
    # Clean unused images
    echo "$(date): Cleaning unused Docker images..." >> "$LOG_FILE"
    docker image prune -f >> "$LOG_FILE" 2>&1 || true
    
    # Clean old logs
    echo "$(date): Cleaning old logs..." >> "$LOG_FILE"
    find /var/log -name "*.gz" -mtime +30 -delete 2>/dev/null || true
    find /opt/westforce/logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Clean apt cache
    apt-get clean >> "$LOG_FILE" 2>&1 || true
    
    # Report new disk usage
    new_disk_usage=$(df / | awk 'NR==2 {print int($5)}')
    freed=$((disk_usage - new_disk_usage))
    echo "$(date): Cleanup complete. Freed approximately ${freed}%. New usage: ${new_disk_usage}%" >> "$LOG_FILE"
fi
CLEANUPSCRIPT

chmod 755 "$SCRIPTS_DIR/westforce-disk-cleanup.sh"
log_info "✓ Disk cleanup script created"

# === CONFIGURE CRONTAB ===
log_step "6/7 - Configuring scheduled tasks (crontab)..."

# Create temporary file with new entries
CRON_FILE=$(mktemp)
crontab -l 2>/dev/null > "$CRON_FILE" || true

# Remove previous Westforce entries if they exist
sed -i '/westforce/d' "$CRON_FILE"

# Add new entries with comprehensive monitoring
cat >> "$CRON_FILE" << EOF
# =============================================================================
# WESTFORCE ZERO-MAINTENANCE MONITORING
# Configured: $(date)
# Healthchecks.io: $HEALTHCHECK_HEARTBEAT_URL
# =============================================================================

# Health check every minute - pings healthchecks.io, auto-recovers if app fails
* * * * * $SCRIPTS_DIR/westforce-healthcheck.sh >> /var/log/westforce-healthcheck.log 2>&1

# Resource monitoring every 5 minutes - alerts if CPU/RAM/Disk too high
*/5 * * * * $SCRIPTS_DIR/westforce-resource-monitor.sh >> /var/log/westforce-resources.log 2>&1

# Docker watchdog every 2 minutes - restarts containers if they crash
*/2 * * * * $SCRIPTS_DIR/westforce-docker-watchdog.sh >> /var/log/westforce-docker-watchdog.log 2>&1

# Daily backup at 3:00 AM (Perth time)
0 3 * * * $SCRIPTS_DIR/westforce-backup.sh >> /var/log/westforce-backup.log 2>&1

# Automatic disk cleanup at 4:00 AM if disk usage is high
0 4 * * * $SCRIPTS_DIR/westforce-disk-cleanup.sh >> /var/log/westforce-cleanup.log 2>&1

# Weekly Docker cleanup on Sundays at 5:00 AM
0 5 * * 0 docker system prune -af --volumes-filter "until=168h" >> /var/log/westforce-docker-cleanup.log 2>&1

# Weekly security updates on Sundays at 6:00 AM (automatic unattended upgrades)
0 6 * * 0 apt-get update && apt-get upgrade -y --with-new-pkgs >> /var/log/westforce-security-updates.log 2>&1
EOF

# Install the new crontab
crontab "$CRON_FILE"
rm "$CRON_FILE"

log_info "✓ Crontab configured with all monitoring tasks"

# === CREATE LOG DIRECTORY ===
log_step "7/7 - Setting up log files and final configuration..."
mkdir -p /var/log
touch /var/log/westforce-healthcheck.log
touch /var/log/westforce-resources.log
touch /var/log/westforce-backup.log
touch /var/log/westforce-docker-watchdog.log
touch /var/log/westforce-cleanup.log
touch /var/log/westforce-docker-cleanup.log
touch /var/log/westforce-security-updates.log

# Set permissions
chmod 644 /var/log/westforce-*.log

# === CONFIGURE LOGROTATE FOR WESTFORCE LOGS ===
log_info "Configuring logrotate..."
cat > /etc/logrotate.d/westforce << EOF
/var/log/westforce-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 640 root root
    sharedscripts
    postrotate
        # Optionally notify healthchecks that logs were rotated
        true
    endscript
}
EOF

# === CONFIGURE UNATTENDED UPGRADES ===
log_info "Configuring unattended security upgrades..."
apt-get install -y unattended-upgrades apt-listchanges > /dev/null 2>&1 || true

cat > /etc/apt/apt.conf.d/50unattended-upgrades << EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}";
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
    "\${distro_id}ESM:\${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

cat > /etc/apt/apt.conf.d/20auto-upgrades << EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF

log_info "✓ Unattended security upgrades configured"

# === CONFIGURE SYSTEMD TO RESTART DOCKER ON FAILURE ===
log_info "Configuring Docker to restart automatically on failure..."
mkdir -p /etc/systemd/system/docker.service.d
cat > /etc/systemd/system/docker.service.d/restart.conf << EOF
[Service]
Restart=always
RestartSec=5s
EOF
systemctl daemon-reload

log_info "✓ Docker auto-restart on failure configured"

# === TEST SCRIPTS ===
log_info "Testing healthcheck script..."
if "$SCRIPTS_DIR/westforce-healthcheck.sh"; then
    log_info "✓ Healthcheck executed successfully"
else
    log_warn "⚠ Healthcheck failed (this may be normal if the app is not running)"
fi

# === SUMMARY ===
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo -e "║  ${GREEN}✅ ZERO-MAINTENANCE MONITORING CONFIGURED${NC}                              ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 SCRIPTS CREATED:"
echo "  ├── $SCRIPTS_DIR/westforce-healthcheck.sh     (every 1 min + auto-recovery)"
echo "  ├── $SCRIPTS_DIR/westforce-resource-monitor.sh (every 5 min + scaling alerts)"
echo "  ├── $SCRIPTS_DIR/westforce-docker-watchdog.sh  (every 2 min + container recovery)"
echo "  ├── $SCRIPTS_DIR/westforce-backup.sh           (daily at 3:00 AM)"
echo "  └── $SCRIPTS_DIR/westforce-disk-cleanup.sh     (daily at 4:00 AM)"
echo ""
echo "📊 HEALTHCHECKS.IO CONFIGURATION:"
echo "  URL: $HEALTHCHECK_HEARTBEAT_URL"
echo ""
echo "  Recommended checks in healthchecks.io:"
echo "  ┌──────────────────────────────────────────────────────────────────────┐"
echo "  │ Name                    │ Schedule     │ Grace    │ Purpose          │"
echo "  ├──────────────────────────────────────────────────────────────────────┤"
echo "  │ westforce-heartbeat     │ * * * * *    │ 5 min    │ App health       │"
echo "  │ westforce-resources     │ */5 * * * *  │ 10 min   │ Resource alerts  │"
echo "  │ westforce-backup        │ 0 3 * * *    │ 1 hour   │ Daily backup     │"
echo "  └──────────────────────────────────────────────────────────────────────┘"
echo ""
echo "🔄 AUTO-RECOVERY FEATURES:"
echo "  ✓ Docker containers restart automatically (restart: unless-stopped)"
echo "  ✓ App auto-restarts after 3 consecutive health check failures"
echo "  ✓ Docker watchdog monitors and restarts crashed containers every 2 min"
echo "  ✓ Docker daemon configured to restart on failure"
echo "  ✓ Automatic disk cleanup when usage exceeds 80%"
echo "  ✓ Automatic security updates (unattended-upgrades)"
echo ""
echo "📝 LOGS:"
echo "  ├── /var/log/westforce-healthcheck.log"
echo "  ├── /var/log/westforce-resources.log"
echo "  ├── /var/log/westforce-backup.log"
echo "  ├── /var/log/westforce-docker-watchdog.log"
echo "  └── /var/log/westforce-cleanup.log"
echo ""
echo "🔧 MANUAL COMMANDS:"
echo "  Check crontab:     sudo crontab -l"
echo "  Test healthcheck:  sudo $SCRIPTS_DIR/westforce-healthcheck.sh"
echo "  Test resources:    sudo $SCRIPTS_DIR/westforce-resource-monitor.sh"
echo "  View logs:         tail -f /var/log/westforce-*.log"
echo ""
echo "⚠️  IMPORTANT: Configure email notifications in healthchecks.io!"
echo "   Go to: Integrations → Add Email → guillermomc007@gmail.com"
echo ""
