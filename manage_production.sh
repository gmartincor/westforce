#!/bin/bash
# =============================================================================
# manage_production.sh - Script para gestionar producción de forma segura
# =============================================================================

set -e  # Salir si hay algún error

echo "🚀 WESTFORCE - Gestión de Producción"
echo "=================================="

# Verificar que existe el archivo .env.production
if [ ! -f .env.production ]; then
    echo "❌ Error: No se encontró .env.production"
    echo "   Crea el archivo con las credenciales de producción"
    exit 1
fi

# Función para mostrar ayuda
show_help() {
    echo "Comandos disponibles:"
    echo ""
    echo "🔧 GESTIÓN DE USUARIOS:"
    echo "  create-superuser     - Crear un superusuario (interactivo)"
    echo "  list-users           - Listar todos los usuarios"
    echo "  set-password         - Cambiar contraseña de un usuario"
    echo ""
    echo "📊 INFORMACIÓN:"
    echo "  migrate              - Aplicar migraciones"
    echo ""
    echo "Ejemplo: ./manage_production.sh create-superuser"
}

# Exportar variables de entorno desde .env.production
export $(grep -v '^#' .env.production | xargs)

case "$1" in
    "create-superuser")
        echo "👑 Creando superusuario para administración..."
        echo "⚠️  Este usuario tendrá acceso completo al sistema"
        echo ""
        echo "💡 RECOMENDACIONES:"
        echo "   - Username: admin, guillermo, o tu nombre preferido"
        echo "   - Email: tu email real (para recuperación)"
        echo "   - Password: mínimo 8 caracteres, usa algo seguro"
        echo ""
        read -p "¿Continuar? (y/n): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            python manage.py createsuperuser
        else
            echo "❌ Operación cancelada"
        fi
        ;;
    
    "list-users")
        echo "👥 Listando usuarios del sistema..."
        python manage.py shell -c "
from apps.authentication.models import User
print('=== SUPERUSUARIOS ===')
for user in User.objects.filter(is_superuser=True):
    print(f'👑 {user.username} ({user.email})')

print('\n=== USUARIOS REGULARES ===')
for user in User.objects.filter(is_superuser=False):
    print(f'👤 {user.username} ({user.email})')
"
        ;;
    
    "set-password")
        echo "🔑 Cambiar contraseña de usuario..."
        read -p "Username: " username
        python manage.py changepassword "$username"
        ;;
    
    "migrate")
        echo "📦 Aplicando migraciones..."
        python manage.py migrate
        ;;
    
    "shell")
        echo "🐍 Abriendo shell de Django..."
        python manage.py shell
        ;;
    
    *)
        show_help
        ;;
esac
