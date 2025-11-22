.PHONY: help dev prod build clean test logs status restart migrate makemigrations shell superuser seed seed-flush mcp-setup deploy-logs deploy-status collectstatic

COMPOSE := docker-compose

help:
	@echo "🐳 Westforce Commands:"
	@echo ""
	@echo "DEVELOPMENT:"
	@echo "  dev          - Start development environment"
	@echo "  build        - Rebuild images"
	@echo "  clean        - Clean containers and volumes"
	@echo "  restart      - Restart services"
	@echo "  collectstatic - Collect static files"
	@echo ""
	@echo "RENDER MCP:"
	@echo "  mcp-setup    - Configure Render MCP"
	@echo "  deploy-logs  - View latest deploy logs"
	@echo "  deploy-status - Service status"
	@echo ""
	@echo "DATABASE:"
	@echo "  migrate      - Run migrations"
	@echo "  makemigrations - Create new migrations"
	@echo "  shell        - Open Django shell"
	@echo "  superuser    - Create superuser"
	@echo "  seed         - Seed development data (manual)"
	@echo "  seed-flush   - Flush and reseed all data"
	@echo ""
	@echo "UTILS:"
	@echo "  test         - Run tests"
	@echo "  logs         - Show logs"
	@echo "  status       - Show container status"
	@echo ""

dev:
	@echo "🚀 Starting development environment..."
	@$(COMPOSE) up --remove-orphans

prod:
	@echo "🏭 Starting production environment..."
	@DJANGO_SETTINGS_MODULE=config.settings.production $(COMPOSE) up --remove-orphans

build:
	@echo "🔨 Rebuilding images..."
	@$(COMPOSE) build --no-cache

clean:
	@echo "🧹 Cleaning containers and volumes..."
	@$(COMPOSE) down -v --remove-orphans
	@docker system prune -f

restart:
	@echo "🔄 Restarting services..."
	@$(COMPOSE) restart

test:
	@echo "🧪 Running tests..."
	@$(COMPOSE) exec web python manage.py test

logs:
	@$(COMPOSE) logs -f web

status:
	@$(COMPOSE) ps

mcp-setup:
	@./scripts/setup-mcp.sh

deploy-logs:
	@./scripts/render-deploy-logs.sh

deploy-status:
	@./scripts/render-service-status.sh

migrate:
	@echo "🔄 Running migrations..."
	@docker exec westforce-web python manage.py migrate --verbosity=2

makemigrations:
	@echo "📝 Creating migrations..."
	@docker exec westforce-web python manage.py makemigrations

shell:
	@echo "🐍 Opening Django shell..."
	@docker exec -it westforce-web python manage.py shell

superuser:
	@echo "👑 Creating superuser..."
	@docker exec -it westforce-web python manage.py createsuperuser

seed:
	@echo "🌱 Seeding development data..."
	@docker exec westforce-web python manage.py seed_dev_data

seed-flush:
	@echo "⚠️  Flushing and reseeding all data..."
	@docker exec westforce-web python manage.py seed_dev_data --flush

collectstatic:
	@echo "📦 Collecting static files..."
	@docker exec westforce-web python manage.py collectstatic --noinput

.DEFAULT_GOAL := help
