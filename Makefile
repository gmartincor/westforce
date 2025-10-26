# =============================================================================
# Westforce - Clean Architecture Commands
# =============================================================================

.PHONY: help dev prod build clean test logs status restart migrate makemigrations shell superuser

COMPOSE_FILE := docker-compose.yml
ENV_FILE_DEV := .env.dev-with-prod-db

help: ## Show available commands
	@echo "🐳 Westforce Commands:"
	@echo ""
	@echo "DEVELOPMENT:"
	@echo "  dev          - Start development environment"
	@echo "  build        - Rebuild images"
	@echo "  clean        - Clean containers and volumes"
	@echo "  restart      - Restart services"
	@echo ""
	@echo "DATABASE:"
	@echo "  migrate      - Run migrations"
	@echo "  makemigrations - Create new migrations"
	@echo "  shell        - Open Django shell"
	@echo "  superuser    - Create superuser"
	@echo ""
	@echo "UTILS:"
	@echo "  test         - Run tests"
	@echo "  logs         - Show logs"
	@echo "  status       - Show container status"
	@echo ""

dev: ## Start development environment
	@echo "🚀 Starting development environment..."
	@docker-compose --env-file $(ENV_FILE_DEV) up --remove-orphans

migrate: ## Run migrations
	@echo "� Running migrations..."
	@docker exec westforce-web-1 python manage.py migrate --verbosity=2

setup: ## Complete setup (migrate + load data)
	@echo "⚙️ Setting up application..."
	@$(MAKE) migrate
	@echo "📊 Loading initial data..."
	@docker exec westforce-web-1 python manage.py loaddata fixtures.json || true
	@echo "✅ Setup complete"

prod: ## Start production environment
	@echo "🏭 Starting production environment..."
	@DJANGO_SETTINGS_MODULE=config.settings.production docker-compose up --remove-orphans

build: ## Rebuild images
	@echo "🔨 Rebuilding images..."
	@docker-compose build --no-cache

clean: ## Clean containers and volumes
	@echo "🧹 Cleaning containers and volumes..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f

restart: ## Restart services
	@echo "🔄 Restarting services..."
	@docker-compose restart

test: ## Run tests
	@echo "🧪 Running tests..."
	@docker-compose exec web python manage.py test

logs: ## Show logs
	@docker-compose logs -f web

status: ## Show container status
	@docker-compose ps

migrate: ## Run migrations
	@echo "🔄 Running migrations..."
	@docker exec westforce-web-1 python manage.py migrate --verbosity=2

makemigrations: ## Create new migrations
	@echo "📝 Creating migrations..."
	@docker exec westforce-web-1 python manage.py makemigrations

shell: ## Open Django shell
	@echo "🐍 Opening Django shell..."
	@docker exec -it westforce-web-1 python manage.py shell

superuser: ## Create superuser
	@echo "👑 Creating superuser..."
	@docker exec -it westforce-web-1 python manage.py createsuperuser

.DEFAULT_GOAL := help
