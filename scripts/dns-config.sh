#!/bin/bash

# =============================================================================
# dns-config.sh - Configuración DNS simplificada para westforce.com
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🌐 Configuración DNS para westforce.com${NC}"
echo "======================================"

echo ""
echo "📋 CONFIGURACIÓN DNS REQUERIDA:"
echo "-------------------------------"

echo ""
echo "1. 📍 DOMINIO PRINCIPAL (westforce.com):"
echo "   Tipo: A"
echo "   Nombre: @"
echo "   Valor: [IP_DE_RENDER] (se obtiene automáticamente)"
echo "   TTL: 300"

echo ""
echo "2. 🔄 SUBDOMINIO WWW (www.westforce.com):"
echo "   Tipo: CNAME"
echo "   Nombre: www"
echo "   Valor: westforce.com"
echo "   TTL: 300"

echo ""
echo "📝 CONFIGURACIÓN SIMPLIFICADA:"
echo "------------------------------"
echo "• westforce.com              (Aplicación completa)"
echo "• www.westforce.com          (Redirect a westforce.com)"

echo ""
echo "⚙️  CONFIGURACIÓN EN RENDER:"
echo "----------------------------"
echo "Repository: https://github.com/gmartincor/westforce"
echo "Branch: main"
echo "1. Agregar dominio personalizado: westforce.com"
echo "2. Verificar configuración DNS"
echo "3. Activar SSL automático"

echo ""
echo "🔧 COMANDOS ÚTILES PARA VERIFICAR DNS:"
echo "--------------------------------------"
echo "• dig westforce.com"
echo "• dig www.westforce.com"
echo "• nslookup westforce.com"

echo ""
echo "✅ CHECKLIST DE CONFIGURACIÓN:"
echo "------------------------------"
echo "□ Dominio principal configurado"
echo "□ SSL/TLS activado"
echo "□ Verificación DNS completada"

echo ""
echo "🎯 RUTAS DE LA APLICACIÓN:"
echo "-------------------------"
echo "• westforce.com/                 → Landing"
echo "• westforce.com/auth/login/      → Login"
echo "• westforce.com/dashboard/       → Dashboard"
echo "• westforce.com/expenses/        → Expenses"
echo "• westforce.com/accounting/      → Accounting"
echo "• westforce.com/invoicing/       → Invoicing"
echo "• westforce.com/admin/           → Admin"

echo ""
echo -e "${GREEN}✅ Configuración DNS simplificada completada${NC}"
echo "==============================================="
echo "   Tipo: CNAME"
echo "   Nombre: manager"
echo "   Valor: westforce.com.au"
echo "   TTL: 300"

echo ""
echo "4. 📧 CONFIGURACIÓN DE EMAIL (MX Records):"
echo "   Tipo: MX"
echo "   Nombre: @"
echo "   Valor: [SERVIDOR_EMAIL] (ej: mx.google.com)"
echo "   Prioridad: 10"
echo "   TTL: 3600"

echo ""
echo "5. 🔒 CONFIGURACIÓN SSL/TLS:"
echo "   - Render maneja automáticamente SSL para dominio principal"
echo "   - Wildcard SSL incluido para subdominios *.westforce.com.au"
echo "   - Certificados Let's Encrypt renovados automáticamente"

echo ""
echo "📝 CONFIGURACIÓN DE DOMINIOS:"
echo "---------------------------------------"
echo "• westforce.com.au              (Landing page)"
echo "• manager.westforce.com.au      (Panel de gestión)"
echo "• manager.westforce.com.au/admin/   (Admin Django)"

echo ""
echo "⚙️  CONFIGURACIÓN EN RENDER:"
echo "----------------------------"
echo "Repository: https://github.com/gmartincor/westforce"
echo "Branch: production"
echo "1. Agregar dominio personalizado: westforce.com.au"
echo "2. Agregar wildcard domain: *.westforce.com.au"
echo "3. Verificar configuración DNS"
echo "4. Activar SSL automático"

echo ""
echo "🔧 COMANDOS ÚTILES PARA VERIFICAR DNS:"
echo "--------------------------------------"
echo "• dig westforce.com.au"
echo "• dig www.westforce.com.au"
echo "• dig manager.westforce.com.au"
echo "• nslookup westforce.com.au"

echo ""
echo "✅ CHECKLIST DE CONFIGURACIÓN:"
echo "------------------------------"
echo "□ Dominio principal configurado"
echo "□ Wildcard subdomain configurado"
echo "□ SSL/TLS activado"
echo "□ MX records configurados (si se usa email)"
echo "□ Verificación DNS completada"
echo "□ Pruebas de subdominios funcionando"

echo ""
echo "🚨 IMPORTANTE:"
echo "-------------"
echo "• Los cambios DNS pueden tardar 24-48 horas en propagarse"
echo "• Usar herramientas como https://whatsmydns.net/ para verificar"
echo "• Configurar primero en un subdominio de prueba si es necesario"

echo ""
echo "📚 DOCUMENTACIÓN:"
echo "----------------"
echo "• Render Custom Domains: https://render.com/docs/custom-domains"
echo "• Django Production: https://docs.djangoproject.com/en/4.2/howto/deployment/"
echo "• SSL Configuration: https://render.com/docs/ssl"

echo ""
echo "🎯 SIGUIENTE PASO: Configurar variables de entorno en Render"
echo "============================================================"
