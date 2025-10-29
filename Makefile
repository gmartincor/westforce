.PHONY: help dev prod build clean test logs status restart migrate makemigrations shell superuser seed seed-flush

COMPOSE := docker-compose
COMPOSE_FILE := docker-compose.yml
ENV_FILE_DEV := .env.dev-with-prod-db

help:
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
	@docker-compose --env-file $(ENV_FILE_DEV) up --remove-orphans

prod:
	@echo "🏭 Starting production environment..."
	@DJANGO_SETTINGS_MODULE=config.settings.production docker-compose up --remove-orphans

build:
	@echo "🔨 Rebuilding images..."
	@docker-compose build --no-cache

clean:
	@echo "🧹 Cleaning containers and volumes..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f

restart:
	@echo "🔄 Restarting services..."
	@docker-compose restart

test:
	@echo "🧪 Running tests..."
	@docker-compose exec web python manage.py test

logs:
	@docker-compose logs -f web

status:
	@docker-compose ps

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

.DEFAULT_GOAL := help
