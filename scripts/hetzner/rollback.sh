#!/usr/bin/env bash
# =============================================================================
# Rollback script for Westforce on Hetzner
# Reverts to a previous version in case of issues
# =============================================================================

set -euo pipefail

APP_DIR="${APP_DIR:-/opt/westforce/app}"
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="/opt/westforce/backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cd "$APP_DIR"

echo "=============================================="
echo "  WESTFORCE ROLLBACK"
echo "=============================================="
echo ""

# Show recent commits
log_info "Last 10 available commits:"
echo ""
git log --oneline -10
echo ""

# Show available Docker images
log_info "Available Docker images:"
docker images | grep westforce | head -10
echo ""

# Show available database backups
log_info "Available database backups:"
ls -lh "$BACKUP_DIR"/*.dump.gz 2>/dev/null | tail -5 || echo "No backups available"
echo ""

# Request confirmation
read -p "Do you want to perform a rollback? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    log_info "Rollback canceled"
    exit 0
fi

# Rollback options
echo ""
echo "Rollback options:"
echo "  1) Code rollback (git checkout to a previous commit)"
echo "  2) Docker image rollback (use a previous image)"
echo "  3) Database rollback (restore a backup)"
echo "  4) Full rollback (code + DB)"
echo ""
read -p "Select an option (1-4): " option

case $option in
    1)
        read -p "Enter the commit hash: " commit_hash
        log_info "Checking out to $commit_hash..."
        git checkout "$commit_hash"
        docker compose -f "$COMPOSE_FILE" up -d --build
        ;;
    2)
        read -p "Enter the image tag: " image_tag
        log_info "Using image $image_tag..."
        export IMAGE_TAG="$image_tag"
        docker compose -f "$COMPOSE_FILE" up -d
        ;;
    3)
        log_info "Available backups:"
        ls -1 "$BACKUP_DIR"/*.dump.gz 2>/dev/null
        read -p "Enter the backup file name: " backup_file
        
        log_warn "⚠️  THIS WILL OVERWRITE THE CURRENT DATABASE"
        read -p "Are you sure? (y/N): " confirm_db
        if [[ "$confirm_db" =~ ^[Yy]$ ]]; then
            log_info "Restoring backup $backup_file..."
            gunzip -c "$BACKUP_DIR/$backup_file" | docker exec -i westforce-postgres pg_restore -U westforce -d westforce_removals --clean --if-exists
            log_info "Database restored"
        fi
        ;;
    4)
        read -p "Enter the commit hash: " commit_hash
        log_info "Available backups:"
        ls -1 "$BACKUP_DIR"/*.dump.gz 2>/dev/null
        read -p "Enter the backup file name: " backup_file
        
        log_warn "⚠️  THIS WILL OVERWRITE BOTH CODE AND DATABASE"
        read -p "Are you sure? (y/N): " confirm_full
        if [[ "$confirm_full" =~ ^[Yy]$ ]]; then
            log_info "Checking out to $commit_hash..."
            git checkout "$commit_hash"
            
            log_info "Rebuilding containers..."
            docker compose -f "$COMPOSE_FILE" up -d --build
            
            log_info "Waiting for the database to be ready..."
            sleep 10
            
            log_info "Restoring backup $backup_file..."
            gunzip -c "$BACKUP_DIR/$backup_file" | docker exec -i westforce-postgres pg_restore -U westforce -d westforce_removals --clean --if-exists
            
            log_info "Full rollback completed"
        fi
        ;;
    *)
        log_error "Invalid option"
        exit 1
        ;;
esac

# Verify application status
log_info "Checking application status..."
sleep 5

if curl -sf http://localhost:8000/health/ > /dev/null 2>&1; then
    log_info "✅ Application is running correctly after the rollback"
else
    log_error "❌ The application is not responding after the rollback"
    log_error "Check the logs: docker compose -f $COMPOSE_FILE logs"
fi
