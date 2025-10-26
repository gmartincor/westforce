ñ#!/bin/bash

# =============================================================================
# dns-config.sh - Configuración DNS para westforce.com.au
# =============================================================================
# Este script proporciona las configuraciones DNS necesarias para
# configurar correctamente los dominios para westforce.com.au

set -e

echo "🌐 Configuración DNS para westforce.com.au"
echo "======================================"

echo ""
echo "📋 CONFIGURACIÓN DNS REQUERIDA:"
echo "-------------------------------"

echo ""
echo "1. 📍 DOMINIO PRINCIPAL (westforce.com.au):"
echo "   Tipo: A"
echo "   Nombre: @"
echo "   Valor: [IP_DE_RENDER] (se obtiene automáticamente)"
echo "   TTL: 300"

echo ""
echo "2. 🔄 SUBDOMINIO WWW (www.westforce.com.au):"
echo "   Tipo: CNAME"
echo "   Nombre: www"
echo "   Valor: westforce.com.au"
echo "   TTL: 300"

echo ""
echo "3. 🏢 DOMINIO MANAGER (manager.westforce.com.au):"
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
