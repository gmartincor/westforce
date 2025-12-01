.PHONY: help dev build clean test logs status restart migrate makemigrations shell superuser seed seed-flush collectstatic setup deploy prod-logs prod-status backup rollback

COMPOSE_DEV := docker compose
COMPOSE_PROD := docker compose -f docker-compose.prod.yml

help:
	@echo "🐳 Westforce Commands:"
	@echo ""
	@echo "DEVELOPMENT:"
	@echo "  dev           - Start development environment"
	@echo "  build         - Rebuild images"
	@echo "  clean         - Clean containers and volumes"
	@echo "  restart       - Restart services"
	@echo "  logs          - Show development logs"
	@echo "  status        - Show container status"
	@echo ""
	@echo "PRODUCTION (Hetzner):"
	@echo "  setup         - Interactive server setup"
	@echo "  deploy        - Deploy to production"
	@echo "  prod-logs     - View production logs"
	@echo "  prod-status   - Check production status"
	@echo "  backup        - Manual backup"
	@echo "  rollback      - Rollback production"
	@echo ""
	@echo "DATABASE:"
	@echo "  migrate       - Run migrations"
	@echo "  makemigrations - Create new migrations"
	@echo "  shell         - Open Django shell"
	@echo "  superuser     - Create superuser"
	@echo "  seed          - Seed development data"
	@echo "  seed-flush    - Flush and reseed all data"
	@echo ""
	@echo "OTHER:"
	@echo "  test          - Run tests"
	@echo "  collectstatic - Collect static files"
	@echo ""

# === DEVELOPMENT ===
dev:
	@echo "🚀 Starting development environment..."
	@$(COMPOSE_DEV) up --remove-orphans

build:
	@echo "🔨 Rebuilding images..."
	@$(COMPOSE_DEV) build --no-cache

clean:
	@echo "🧹 Cleaning containers and volumes..."
	@$(COMPOSE_DEV) down -v --remove-orphans
	@docker system prune -f

restart:
	@echo "🔄 Restarting services..."
	@$(COMPOSE_DEV) restart

logs:
	@$(COMPOSE_DEV) logs -f web

status:
	@$(COMPOSE_DEV) ps

# === PRODUCTION (HETZNER) ===
setup:
	@echo "🚀 Starting server setup..."
	@./scripts/hetzner/00-interactive-setup.sh

deploy:
	@echo "🚀 Deploying to production..."
	@./scripts/hetzner/02-deploy.sh

prod-logs:
	@echo "📋 Production logs..."
	@$(COMPOSE_PROD) logs -f

prod-status:
	@echo "📊 Production status..."
	@$(COMPOSE_PROD) ps

backup:
	@echo "💾 Running backup..."
	@$(COMPOSE_PROD) --profile backup run --rm db-backup

rollback:
	@echo "⏪ Starting rollback..."
	@./scripts/hetzner/rollback.sh

# === DATABASE ===
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

# === OTHER ===
test:
	@echo "🧪 Running tests..."
	@$(COMPOSE_DEV) exec web python manage.py test

collectstatic:
	@echo "📦 Collecting static files..."
	@docker exec westforce-web python manage.py collectstatic --noinput

.DEFAULT_GOAL := help
