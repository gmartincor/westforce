#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly LOG_FILE="${LOG_FILE:-/tmp/deployment.log}"
readonly ENVIRONMENT="${ENVIRONMENT:-production}"

source "${SCRIPT_DIR}/lib/logging.sh"
source "${SCRIPT_DIR}/lib/database.sh"
source "${SCRIPT_DIR}/lib/django.sh"

trap 'handle_error ${LINENO}' ERR

main() {
    local SKIP_STATIC=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-static) SKIP_STATIC=true; shift ;;
            -h|--help) echo "Usage: $0 [--skip-static]"; exit 0 ;;
            *) log_warning "Unknown option: $1"; shift ;;
        esac
    done
    
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    log_info "Starting deployment process..."
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Django settings: ${DJANGO_SETTINGS_MODULE:-not set}"
    
    local python_cmd=$(get_python_cmd)
    
    if [[ ! -f "manage.py" ]]; then
        log_error "manage.py not found in $(pwd)"
        exit 1
    fi
    
    if [[ -z "${DJANGO_SETTINGS_MODULE:-}" ]]; then
        log_error "DJANGO_SETTINGS_MODULE not set"
        exit 1
    fi
    
    log_info "Step 1/4: Waiting for database..."
    wait_for_database "$python_cmd"
    
    log_info "Step 2/4: Running migrations..."
    run_migrations "$python_cmd"
    create_cache_table "$python_cmd"
    
    log_info "Step 3/4: Verifying CSS..."
    if [[ ! -f "static/css/style.css" ]]; then
        log_error "CSS file missing: static/css/style.css"
        exit 1
    fi
    local css_size=$(stat -c%s "static/css/style.css" 2>/dev/null || stat -f%z "static/css/style.css" 2>/dev/null || echo "0")
    if [[ "$css_size" -lt 100 ]]; then
        log_error "CSS file appears corrupted"
        exit 1
    fi
    log_info "CSS verified (${css_size} bytes)"
    
    if [[ "$SKIP_STATIC" != "true" ]]; then
        log_info "Step 4/4: Collecting static files..."
        collect_static_files "$python_cmd"
    else
        log_info "Step 4/4: Skipping static files collection"
    fi
    
    verify_django_config "$python_cmd" || log_warning "Some Django checks failed"
    
    log_info "Deployment completed successfully"
    return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
