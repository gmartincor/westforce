# =============================================================================
# Makefile - Westforce Commands (Fases 1-4)
# =============================================================================

.PHONY: help dev full-dev prod build clean test logs deploy verify-prod

# Variables
COMPOSE_FILE := docker-compose.yml
PROJECT_NAME := westforce

# =============================================================================
# HELP
# =============================================================================
help: ## Mostrar ayuda
	@echo "🐳 Westforce - Comandos disponibles:"
	@echo ""
	@echo "DESARROLLO:"
	@echo "  dev          - Desarrollo normal (con BD de producción)"
	@echo "  dev-empty    - Desarrollo con BD vacía (solo si necesitas empezar de cero)"
	@echo "  full-dev     - Desarrollo completo (PostgreSQL + Redis + App)"
	@echo "  build        - Rebuild imágenes"
	@echo "  clean        - Limpiar containers y volúmenes"
	@echo "  test         - Ejecutar tests"
	@echo "  logs         - Ver logs"
	@echo ""
	@echo "SINCRONIZACIÓN BD:"
	@echo "  backup-local - Backup BD local actual"
	@echo ""
	@echo "PRODUCCIÓN:"
	@echo "  verify-prod  - Verificar configuración de producción"
	@echo "  deploy       - Deploy a Render"
	@echo ""
	@echo "  clean        - Limpiar contenedores"
	@echo "  test         - Ejecutar tests"
	@echo "  logs         - Ver logs"
	@echo "  setup        - Configurar entorno inicial"
	@echo ""

# =============================================================================
# DEVELOPMENT
# =============================================================================
dev: ## Desarrollo normal (con BD de producción)
	@echo "🚀 Iniciando desarrollo con BD de producción..."
	@echo "💡 BD con todos los datos reales de producción"
	@docker-compose --env-file .env.dev-with-prod-db --profile dev-synced up --remove-orphans

dev-empty: ## Desarrollo con BD vacía (solo si necesitas empezar de cero)
	@echo "🚀 Iniciando desarrollo con BD vacía..."
	@echo "⚠️  Solo usar si necesitas BD completamente nueva"
	@docker-compose --profile dev up --remove-orphans

full-dev: ## Desarrollo completo
	@echo "🚀 Iniciando desarrollo completo..."
	@docker-compose --profile full-dev up --remove-orphans

# =============================================================================
# PRODUCTION
# =============================================================================
prod: ## Producción
	@echo "🏭 Iniciando producción..."
	@docker-compose --profile prod up --remove-orphans

# =============================================================================
# BUILD & MAINTENANCE
# =============================================================================
build: ## Rebuild imágenes
	@echo "🔨 Rebuilding imágenes..."
	@docker-compose build --no-cache

clean: ## Limpiar contenedores
	@echo "🧹 Limpiando contenedores..."
	@docker-compose down -v --remove-orphans

# =============================================================================
# TESTING
# =============================================================================
test: ## Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	@docker-compose --profile dev run --rm app-dev python manage.py test

test-charts: ## Verificar configuración de charts
	@echo "📊 Verificando configuración de charts..."
	@./scripts/test-charts.sh

# =============================================================================
# UTILS
# =============================================================================
logs: ## Ver logs
	@docker-compose logs -f app-dev

setup: ## Configurar entorno inicial
	@echo "⚙️ Configurando entorno inicial..."
	@./scripts/setup.sh

# =============================================================================
# SHORTCUTS & QUICK COMMANDS
# =============================================================================
up: dev ## Alias para 'dev'
down: ## Parar servicios
	@docker-compose down

# Comandos rápidos para desarrollo diario
migrate: ## Ejecutar migraciones
	@echo "🔄 Ejecutando migraciones..."
	@docker exec westforce_dev_synced_app_dev python manage.py migrate

makemigrations: ## Crear nuevas migraciones
	@echo "📝 Creando migraciones..."
	@docker exec westforce_dev_synced_app_dev python manage.py makemigrations

shell: ## Abrir shell de Django
	@echo "🐍 Abriendo shell de Django..."
	@docker exec -it westforce_dev_synced_app_dev python manage.py shell

superuser: ## Crear superusuario de desarrollo
	@echo "👑 Creando superusuario..."
	@docker exec westforce_dev_synced_app_dev python manage.py create_single_user --force

status: ## Ver estado de contenedores
	@echo "📊 Estado de contenedores:"
	@docker-compose ps

restart: ## Reiniciar aplicación
	@echo "🔄 Reiniciando aplicación..."
	@docker-compose restart app-dev

backup-local: ## Hacer backup de BD local
	@echo "� Haciendo backup de BD local..."
	@docker-compose exec postgres pg_dump -U guillermomartincorrea -d crm_nutricion_pro > "./backups/local_backup_$(date +'%Y%m%d_%H%M%S').sql"

verify-prod: ## Verificar configuración de producción
	@echo "🔍 Verificando configuración de producción..."
	python manage.py check_production_ready

deploy: ## Preparar para deploy en Render
	@echo "🚀 Preparando deploy para Render..."
	@echo "1. Verificando configuración..."
	python manage.py check_production_ready
	@echo "2. Ejecutando tests..."
	python manage.py test --keepdb --parallel
	@echo "3. Listo para deploy en Render"
	@echo "   - Hacer push a branch 'production'"
	@echo "   - Configurar variables de entorno en Render"
	@echo "   - Activar deploy automático"

# Default target
.DEFAULT_GOAL := help
