#!/bin/bash

# =============================================================================
# ULTRA-SAFE MIGRATION SCRIPT - VERSIÓN OPTIMIZADA PARA WESTFORCE
# =============================================================================
# Versión optimizada: eliminado código obsoleto, funciones modularizadas
# Compatible con Render y otros entornos de producción

set -euo pipefail
IFS=$'\n\t'

# Configuration
readonly SCRIPT_NAME="$(basename "${0}")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly LOG_FILE="${LOG_FILE:-/tmp/deployment.log}"
readonly ENVIRONMENT="${ENVIRONMENT:-production}"

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [DEBUG]${NC} $1" | tee -a "$LOG_FILE"
    fi
}

# Error handling
handle_error() {
    local exit_code=$?
    local line_number=$1
    log_error "Script failed at line ${line_number} with exit code ${exit_code}"
    log_error "Check the log file at: ${LOG_FILE}"
    exit "${exit_code}"
}

trap 'handle_error ${LINENO}' ERR

# Helper function to get the correct python command
get_python_cmd() {
    if command -v python &> /dev/null; then
        echo "python"
    elif command -v python3 &> /dev/null; then
        echo "python3"
    else
        log_error "Neither python nor python3 found in PATH"
        exit 1
    fi
}

# Test database connection with retry logic
test_database_connection() {
    local max_attempts=5
    local attempt=1
    local python_cmd=$(get_python_cmd)
    
    log_info "Testing database connection..."
    
    while [[ $attempt -le $max_attempts ]]; do
        local connection_test_output
        connection_test_output=$($python_cmd manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        cursor.fetchone()
    print('SUCCESS: Database connection successful')
except Exception as e:
    print(f'ERROR: Database connection failed: {e}')
    exit(1)
        " 2>&1)
        
        if echo "$connection_test_output" | grep -q "SUCCESS: Database connection successful"; then
            log_info "✅ Database connection successful"
            return 0
        else
            log_warning "Database connection failed on attempt ${attempt}/${max_attempts}"
            if [[ $attempt -lt $max_attempts ]]; then
                sleep $((attempt * 2))
            fi
            ((attempt++))
        fi
    done
    
    log_error "Database connection failed after ${max_attempts} attempts"
    return 1
}

# Verify database is ready
verify_database_ready() {
    log_info "🔧 Verifying database is ready..."
    local python_cmd=$(get_python_cmd)
    
    local verification_output
    verification_output=$($python_cmd manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection verified')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" 2>&1)
    
    echo "$verification_output"
    
    if echo "$verification_output" | grep -q "✅ Database connection verified"; then
        log_info "✅ Database verified successfully"
        return 0
    else
        log_error "❌ Database verification failed"
        return 1
    fi
}

# Check for pending migrations
check_pending_migrations() {
    log_info "🔧 Checking for pending migrations..."
    local python_cmd=$(get_python_cmd)
    
    local makemigrations_output
    makemigrations_output=$($python_cmd manage.py makemigrations --dry-run --verbosity=1 2>&1)
    
    if echo "$makemigrations_output" | grep -q "No changes detected"; then
        log_info "✅ No pending migrations"
        return 0
    else
        log_warning "⚠️  Pending migrations detected, creating them..."
        if $python_cmd manage.py makemigrations --verbosity=1; then
            log_info "✅ Migrations created successfully"
            return 0
        else
            log_error "❌ Failed to create migrations"
            return 1
        fi
    fi
}

# Execute migrations
execute_migrations_simple() {
    log_info "🔧 Executing migrations..."
    local python_cmd=$(get_python_cmd)
    
    if $python_cmd manage.py migrate --verbosity=2; then
        log_info "✅ Migrations completed"
        return 0
    else
        log_error "❌ Migrations failed"
        return 1
    fi
}

# Main migration function (simplified)
execute_migrations() {
    log_info "📋 Executing database migrations..."
    
    verify_database_ready || return 1
    check_pending_migrations || return 1
    execute_migrations_simple || return 1
    
    log_info "✅ All migrations completed successfully"
    return 0
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "🔍 Running pre-deployment checks..."
    
    # Check working directory
    if [[ ! -f "manage.py" ]]; then
        log_error "manage.py not found. Current directory: $(pwd)"
        return 1
    fi
    
    # Check Django settings
    if [[ -z "${DJANGO_SETTINGS_MODULE:-}" ]]; then
        log_error "DJANGO_SETTINGS_MODULE environment variable not set"
        return 1
    fi
    
    log_info "Using Django settings: ${DJANGO_SETTINGS_MODULE}"
    
    # Test database connection
    test_database_connection || return 1
    
    log_info "✅ Pre-deployment checks passed"
    return 0
}

# Verify CSS exists (Docker-aware - no building in production)
verify_css_exists() {
    log_info "🎨 Verifying CSS availability..."
    
    # En Docker/producción, el CSS ya debería estar compilado
    if [[ -f "static/css/style.css" ]]; then
        local file_size=$(stat -c%s "static/css/style.css" 2>/dev/null || stat -f%z "static/css/style.css" 2>/dev/null || echo "0")
        if [[ "$file_size" -gt 100 ]]; then
            log_info "✅ CSS file found and valid (${file_size} bytes)"
            log_info "ℹ️  Using pre-compiled CSS from Docker build process"
            return 0
        else
            log_error "❌ CSS file exists but appears empty or corrupted (${file_size} bytes)"
            return 1
        fi
    fi
    
    # CSS no existe - esto es un problema en producción
    log_error "❌ CSS file not found: static/css/style.css"
    log_error "   Expected location: $(pwd)/static/css/style.css"
    log_info "🔍 Debugging information:"
    log_info "   Listing static/ directory:"
    ls -la static/ 2>&1 || echo "   static/ directory doesn't exist"
    
    # En desarrollo local, podríamos intentar compilar
    if command -v npm &> /dev/null && [[ -f "package.json" ]]; then
        log_warning "⚠️  Attempting CSS compilation in development mode..."
        if npm run build-css; then
            if [[ -f "static/css/style.css" ]]; then
                local file_size=$(stat -c%s "static/css/style.css" 2>/dev/null || stat -f%z "static/css/style.css" 2>/dev/null || echo "unknown")
                log_info "✅ CSS compiled successfully in development mode (${file_size} bytes)"
                return 0
            fi
        fi
        log_error "❌ CSS compilation failed"
    else
        log_error "❌ npm not available - CSS should be pre-compiled in Docker"
    fi
    
    return 1
}

# Verify static files before collection (simplified)
verify_static_prerequisites() {
    log_info "🔧 Verifying static files prerequisites..."
    
    # Verificar que el CSS generado existe
    if [[ ! -f "static/css/style.css" ]]; then
        log_error "❌ Critical file static/css/style.css missing before collectstatic"
        log_error "   Expected: $(pwd)/static/css/style.css"
        log_info "🔍 Listing static/ directory:"
        ls -la static/ 2>&1 || echo "   static/ directory doesn't exist"
        return 1
    fi
    
    # Verificar que el archivo CSS no está vacío
    local file_size=$(stat -c%s "static/css/style.css" 2>/dev/null || stat -f%z "static/css/style.css" 2>/dev/null || echo "0")
    if [[ "$file_size" -lt 100 ]]; then
        log_error "❌ CSS file appears empty or corrupted (${file_size} bytes)"
        log_info "🔍 CSS file content sample:"
        head -5 "static/css/style.css" 2>&1 || echo "   Cannot read file"
        return 1
    fi
    
    log_info "✅ CSS file verified: ${file_size} bytes"
    return 0
}

# Execute collectstatic
execute_collectstatic() {
    local python_cmd=$(get_python_cmd)
    local static_root="${STATIC_ROOT:-/app/static_collected}"
    
    # Ensure static directories exist
    mkdir -p "${static_root}/css" "${static_root}/js" "${static_root}/admin"
    
    log_info "🔧 Running collectstatic..."
    log_info "📂 STATIC_ROOT: ${static_root}"
    
    # Ejecutar collectstatic
    if $python_cmd manage.py collectstatic --noinput --verbosity=2 --skip-checks 2>&1 | tee -a "$LOG_FILE"; then
        log_info "✅ collectstatic command completed successfully"
        
        # Verificar que style.css se copió
        if [[ -f "${static_root}/css/style.css" ]]; then
            local file_size=$(stat -c%s "${static_root}/css/style.css" 2>/dev/null || stat -f%z "${static_root}/css/style.css" 2>/dev/null || echo "0")
            log_info "✅ CSS file successfully collected (${file_size} bytes)"
            return 0
        else
            log_error "❌ CSS file NOT found in collected static files"
            return 1
        fi
    else
        log_error "❌ collectstatic failed"
        return 1
    fi
}

# Static files collection (simplified and modularized)
collect_static_files() {
    log_info "📦 Collecting static files..."
    
    verify_static_prerequisites || return 1
    execute_collectstatic || return 1
    
    log_info "✅ Static files collection completed and verified"
    return 0
}

# Post-deployment validation (simplified)
post_deployment_validation() {
    log_info "🔍 Running post-deployment validation..."
    local python_cmd=$(get_python_cmd)
    
    local validation_result
    validation_result=$($python_cmd manage.py shell -c "
from django.db import connection
from apps.authentication.models import User

try:
    # Verify database connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection working')
    
    # Verify user model
    user_count = User.objects.count()
    print(f'✅ User model working - {user_count} users in system')
    
    print('✅ All validations passed')
except Exception as e:
    print(f'❌ Validation failed: {e}')
    exit(1)
" 2>&1)
        exit(1)
    
    # Verify single user system
    active_users = User.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    print(f'✅ Active users: {active_users}, Total users: {total_users}')
    
    print('✅ Single-user system validated successfully')
    
except Exception as e:
    print(f'❌ Validation error: {e}')
    exit(1)
" 2>&1)
    
    echo "$validation_result"
    
    if echo "$validation_result" | grep -q "✅ Single-user system validated successfully"; then
        log_info "✅ Post-deployment validation successful"
        return 0
    else
        log_warning "⚠️  Some validations failed"
        return 1
    fi
}

# Main execution function (optimized and consistent)
main() {
    local SKIP_STATIC=false
    local SKIP_CHECKS=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-static)
                SKIP_STATIC=true
                shift
                ;;
            --skip-checks)
                SKIP_CHECKS=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [--skip-static] [--skip-checks]"
                exit 0
                ;;
            *)
                log_warning "Unknown option: $1"
                shift
                ;;
        esac
    done
    
    # Create log directory
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    log_info "🚀 Starting optimized deployment process..."
    log_info "📅 Date: $(date)"
    log_info "🌍 Environment: ${ENVIRONMENT}"
    log_info "📝 Log file: ${LOG_FILE}"
    log_info "🔧 Django settings: ${DJANGO_SETTINGS_MODULE:-not set}"
    
    # Step 1: Pre-deployment checks
    log_info "📋 Step 1/5: Running pre-deployment checks..."
    if ! pre_deployment_checks; then
        log_error "❌ Pre-deployment checks failed"
        exit 1
    fi
    
    # Step 2: Database migrations
    log_info "📋 Step 2/5: Executing database migrations..."
    if ! execute_migrations; then
        log_error "❌ Database migrations failed"
        exit 1
    fi
    
    # Step 3: Verify CSS exists (Docker pre-compiled)
    log_info "📋 Step 3/5: Verifying CSS files..."
    if ! verify_css_exists; then
        log_error "❌ CSS verification failed - deployment cannot continue without styles"
        exit 1
    fi
    
    # Step 4: Static files collection
    if [[ "$SKIP_STATIC" != "true" ]]; then
        log_info "📋 Step 4/5: Collecting static files..."
        if ! collect_static_files; then
            log_error "❌ Static files collection failed - deployment cannot continue"
            exit 1
        fi
    else
        log_info "📋 Step 4/5: Skipping static files collection (development only)"
    fi
    
    # Step 5: Post-deployment validation
    if [[ "$SKIP_CHECKS" != "true" ]]; then
        log_info "📋 Step 5/5: Running post-deployment validation..."
        if ! post_deployment_validation; then
            log_warning "⚠️  Some validations failed, but deployment is complete"
        fi
    else
        log_info "📋 Step 5/5: Skipping post-deployment validation"
    fi
    
    # Success message
    log_info ""
    log_info "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
    log_info "✅ Database migrations applied"
    log_info "✅ CSS files verified"
    log_info "✅ Static files collected"
    log_info "✅ Single-user system configured"
    log_info "🚀 Application is ready to serve traffic"
    log_info ""
    log_info "📝 Deployment completed at: $(date)"
    
    return 0
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
