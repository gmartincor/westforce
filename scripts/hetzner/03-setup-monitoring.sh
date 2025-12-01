#!/usr/bin/env bash
# =============================================================================
# Monitoring configuration script for Westforce
# Configures healthchecks.io for heartbeat and resource monitoring
# Run as root or with sudo
# =============================================================================

set -euo pipefail

# === CONFIGURATION ===
SCRIPTS_DIR="/usr/local/bin"
APP_DIR="${APP_DIR:-/opt/westforce/app}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# === VERIFY SCRIPT IS RUN AS ROOT ===
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root or with sudo"
    exit 1
fi

# === LOAD ENVIRONMENT VARIABLES ===
if [[ -f "$APP_DIR/.env" ]]; then
    source "$APP_DIR/.env"
else
    log_error "The .env file was not found in $APP_DIR"
    log_error "The variables HEALTHCHECK_HEARTBEAT_URL and HEALTHCHECK_FAILURE_URL are required"
    exit 1
fi

# Verify required variables
: "${HEALTHCHECK_HEARTBEAT_URL:?Variable HEALTHCHECK_HEARTBEAT_URL not defined}"
: "${HEALTHCHECK_FAILURE_URL:?Variable HEALTHCHECK_FAILURE_URL not defined}"

log_info "=== Configuring Westforce monitoring ==="

# === CREATE HEARTBEAT SCRIPT ===
log_info "Creating heartbeat script..."
cat > "$SCRIPTS_DIR/westforce-healthcheck.sh" << 'HEALTHSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

# Load configuration
source /opt/westforce/app/.env

HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/health/}"
SUCCESS_PING="${HEALTHCHECK_HEARTBEAT_URL}"
FAILURE_PING="${HEALTHCHECK_FAILURE_URL}"

# Check if the health endpoint responds correctly
if curl --silent --max-time 10 --fail "$HEALTH_URL" >/dev/null 2>&1; then
    # Application is healthy - send success ping
    curl --silent --max-time 5 "$SUCCESS_PING" >/dev/null 2>&1 || true
else
    # Application is not responding - send failure ping
    curl --silent --max-time 5 "$FAILURE_PING" >/dev/null 2>&1 || true
fi
HEALTHSCRIPT

chmod 755 "$SCRIPTS_DIR/westforce-healthcheck.sh"
log_info "✓ Heartbeat script created: $SCRIPTS_DIR/westforce-healthcheck.sh"

# === CREATE RESOURCE MONITORING SCRIPT ===
log_info "Creating resource monitoring script..."
cat > "$SCRIPTS_DIR/westforce-resource-monitor.sh" << 'RESOURCESCRIPT'
#!/usr/bin/env bash
set -euo pipefail

# Load configuration
source /opt/westforce/app/.env

# Configurable thresholds (default: alert if exceeding 90%)
CPU_THRESHOLD="${CPU_THRESHOLD:-90}"
RAM_THRESHOLD="${RAM_THRESHOLD:-90}"
DISK_THRESHOLD="${DISK_THRESHOLD:-85}"
FAILURE_PING="${HEALTHCHECK_FAILURE_URL}"

# Get CPU usage (1-second average)
cpu_usage=$(top -bn2 -d1 | grep "Cpu(s)" | tail -1 | awk '{print int(100 - $8)}')

# Get RAM usage
ram_usage=$(free | awk '/Mem:/ {printf("%.0f", $3/$2*100)}')

# Get disk usage
disk_usage=$(df / | awk 'NR==2 {print int($5)}')

# Prepare alert message if any threshold is exceeded
alert_needed=false
alert_msg=""

if (( cpu_usage >= CPU_THRESHOLD )); then
    alert_needed=true
    alert_msg+="CPU=${cpu_usage}% "
fi

if (( ram_usage >= RAM_THRESHOLD )); then
    alert_needed=true
    alert_msg+="RAM=${ram_usage}% "
fi

if (( disk_usage >= DISK_THRESHOLD )); then
    alert_needed=true
    alert_msg+="DISK=${disk_usage}% "
fi

# Send alert if necessary
if [[ "$alert_needed" == true ]]; then
    curl --silent --max-time 5 --data-raw "$alert_msg" "$FAILURE_PING" >/dev/null 2>&1 || true
    echo "$(date): ALERT - $alert_msg" >> /var/log/westforce-resources.log
fi
RESOURCESCRIPT

chmod 755 "$SCRIPTS_DIR/westforce-resource-monitor.sh"
log_info "✓ Resource monitoring script created: $SCRIPTS_DIR/westforce-resource-monitor.sh"

# === CREATE AUTOMATIC BACKUP SCRIPT ===
log_info "Creating backup script..."
cat > "$SCRIPTS_DIR/westforce-backup.sh" << 'BACKUPSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/opt/westforce/backups"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
DATE=$(date +%Y%m%d_%H%M%S)

# Load configuration
source /opt/westforce/app/.env

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform database backup
echo "$(date): Starting database backup..."
docker exec westforce-postgres pg_dump -U "${DB_USER:-westforce}" "${DB_NAME:-westforce_removals}" -Fc > "$BACKUP_DIR/db_$DATE.dump"

# Compress backup
gzip "$BACKUP_DIR/db_$DATE.dump"

# Backup media files (if they exist)
if docker volume ls | grep -q westforce_prod_media_data; then
    echo "$(date): Backing up media files..."
    docker run --rm -v westforce_prod_media_data:/data -v "$BACKUP_DIR":/backup alpine \
        tar czf "/backup/media_$DATE.tar.gz" -C /data .
fi

# Delete old backups
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "$(date): Backup completed successfully"
ls -lh "$BACKUP_DIR" | tail -10
BACKUPSCRIPT

chmod 755 "$SCRIPTS_DIR/westforce-backup.sh"
log_info "✓ Backup script created: $SCRIPTS_DIR/westforce-backup.sh"

# === CONFIGURE CRONTAB ===
log_info "Configuring scheduled tasks (crontab)..."

# Create temporary file with new entries
CRON_FILE=$(mktemp)
crontab -l 2>/dev/null > "$CRON_FILE" || true

# Remove previous Westforce entries if they exist
sed -i '/westforce/d' "$CRON_FILE"

# Add new entries
cat >> "$CRON_FILE" << EOF
# Westforce - Health check every minute
* * * * * $SCRIPTS_DIR/westforce-healthcheck.sh >> /var/log/westforce-healthcheck.log 2>&1

# Westforce - Resource monitoring every 5 minutes
*/5 * * * * $SCRIPTS_DIR/westforce-resource-monitor.sh >> /var/log/westforce-resources.log 2>&1

# Westforce - Daily backup at 3:00 AM
0 3 * * * $SCRIPTS_DIR/westforce-backup.sh >> /var/log/westforce-backup.log 2>&1

# Westforce - Clean Docker logs weekly
0 4 * * 0 docker system prune -f >> /var/log/westforce-docker-cleanup.log 2>&1
EOF

# Install the new crontab
crontab "$CRON_FILE"
rm "$CRON_FILE"

log_info "✓ Crontab configured"

# === CREATE LOG DIRECTORY ===
mkdir -p /var/log
touch /var/log/westforce-healthcheck.log
touch /var/log/westforce-resources.log
touch /var/log/westforce-backup.log

# === CONFIGURE LOGROTATE FOR WESTFORCE LOGS ===
log_info "Configuring logrotate..."
cat > /etc/logrotate.d/westforce << EOF
/var/log/westforce-*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 640 root root
}
EOF

# === TEST SCRIPTS ===
log_info "Testing healthcheck script..."
if "$SCRIPTS_DIR/westforce-healthcheck.sh"; then
    log_info "✓ Healthcheck executed successfully"
else
    log_warn "⚠ Healthcheck failed (this may be normal if the app is not running)"
fi

# === SUMMARY ===
echo ""
echo "=============================================="
echo -e "${GREEN}✅ MONITORING CONFIGURED${NC}"
echo "=============================================="
echo ""
echo "Scripts created:"
echo "  - $SCRIPTS_DIR/westforce-healthcheck.sh (every 1 min)"
echo "  - $SCRIPTS_DIR/westforce-resource-monitor.sh (every 5 min)"
echo "  - $SCRIPTS_DIR/westforce-backup.sh (daily at 3:00 AM)"
echo ""
echo "Logs:"
echo "  - /var/log/westforce-healthcheck.log"
echo "  - /var/log/westforce-resources.log"
echo "  - /var/log/westforce-backup.log"
echo ""
echo "Check crontab: sudo crontab -l"
echo ""
echo "To test manually:"
echo "  sudo $SCRIPTS_DIR/westforce-healthcheck.sh"
echo "  sudo $SCRIPTS_DIR/westforce-resource-monitor.sh"
echo "  sudo $SCRIPTS_DIR/westforce-backup.sh"
echo ""
