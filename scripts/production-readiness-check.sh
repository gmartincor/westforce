#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Westforce Production Readiness Check${NC}"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
    else
        echo -e "${RED}❌${NC} $2"
        ((ERRORS++))
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $2"
    else
        echo -e "${YELLOW}⚠️${NC}  $2"
        ((WARNINGS++))
    fi
}

echo "📁 File Structure:"
check_file "Dockerfile" "Dockerfile exists"
check_file ".dockerignore" ".dockerignore exists"
check_file "requirements.txt" "requirements.txt exists"
check_file "gunicorn.conf.py" "Gunicorn config exists"
check_file "render.yaml" "Render config exists"
check_file ".env.production.example" "Production env example exists"

echo ""
echo "📦 Django Apps:"
check_directory "apps/authentication" "Authentication app"
check_directory "apps/core" "Core app"
check_directory "apps/dashboard" "Dashboard app"
check_directory "apps/accounting" "Accounting app"
check_directory "apps/expenses" "Expenses app"
check_directory "apps/invoicing" "Invoicing app"

echo ""
echo "⚙️  Configuration Files:"
check_file "config/settings/base.py" "Base settings"
check_file "config/settings/production.py" "Production settings"
check_file "config/wsgi.py" "WSGI config"
check_file "config/urls.py" "URL config"

echo ""
echo "🔧 Scripts:"
check_file "scripts/docker-entrypoint.sh" "Docker entrypoint"
if [ -f "scripts/docker-entrypoint.sh" ]; then
    if [ -x "scripts/docker-entrypoint.sh" ]; then
        echo -e "${GREEN}✅${NC} Entrypoint is executable"
    else
        echo -e "${YELLOW}⚠️${NC}  Entrypoint needs execute permission"
        ((WARNINGS++))
    fi
fi

echo ""
echo "🔍 Security Checks:"

if grep -q "DEBUG.*=.*False" config/settings/production.py 2>/dev/null; then
    echo -e "${GREEN}✅${NC} DEBUG=False in production"
else
    echo -e "${RED}❌${NC} DEBUG not False in production"
    ((ERRORS++))
fi

if grep -q "SECURE_SSL_REDIRECT.*=.*True" config/settings/production.py 2>/dev/null; then
    echo -e "${GREEN}✅${NC} SSL redirect enabled"
else
    echo -e "${YELLOW}⚠️${NC}  SSL redirect not configured"
    ((WARNINGS++))
fi

if grep -q "SECURE_HSTS_SECONDS" config/settings/production.py 2>/dev/null; then
    echo -e "${GREEN}✅${NC} HSTS configured"
else
    echo -e "${YELLOW}⚠️${NC}  HSTS not configured"
    ((WARNINGS++))
fi

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️${NC}  .env file exists (ensure it's in .gitignore)"
    ((WARNINGS++))
else
    echo -e "${GREEN}✅${NC} No .env file in root"
fi

if grep -q "\.env" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅${NC} .env is in .gitignore"
else
    echo -e "${RED}❌${NC} .env not in .gitignore"
    ((ERRORS++))
fi

echo ""
echo "🐳 Docker Configuration:"
if grep -q "DJANGO_SETTINGS_MODULE=config.settings.production" Dockerfile 2>/dev/null; then
    echo -e "${GREEN}✅${NC} Production settings in Dockerfile"
else
    echo -e "${YELLOW}⚠️${NC}  Production settings not set in Dockerfile"
    ((WARNINGS++))
fi

if [ -f ".dockerignore" ]; then
    if grep -q "\.env" .dockerignore; then
        echo -e "${GREEN}✅${NC} .env in .dockerignore"
    else
        echo -e "${YELLOW}⚠️${NC}  .env not in .dockerignore"
        ((WARNINGS++))
    fi
fi

echo ""
echo "📊 Database:"
check_directory "apps/authentication/migrations" "Authentication migrations"
check_directory "apps/accounting/migrations" "Accounting migrations"
check_directory "apps/expenses/migrations" "Expenses migrations"
check_directory "apps/invoicing/migrations" "Invoicing migrations"

echo ""
echo "=========================================="
echo -e "${BLUE}Summary:${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Application is ready for production.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  ${WARNINGS} warning(s) found. Review before deploying.${NC}"
    exit 0
else
    echo -e "${RED}❌ ${ERRORS} error(s) found. Fix before deploying.${NC}"
    echo -e "${YELLOW}⚠️  ${WARNINGS} warning(s) found.${NC}"
    exit 1
fi
