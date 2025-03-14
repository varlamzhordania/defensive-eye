# Variables
DOCKER_COMPOSE=docker compose
PROJECT_NAME=core
STRIPE_WEBHOOK_URL=http://localhost:8000/stripe/webhook/

# Default target based on OS detection
initial: detect-os

# Windows initial setup
initial-windows: copy-env-windows build migrations migrate up

# Ubuntu/Linux initial setup
initial-linux: copy-env-linux build migrations migrate up

# OS detection to run the right target
detect-os:
	@echo "Detecting OS..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		$(MAKE) initial-windows; \
	else \
		$(MAKE) initial-linux; \
	fi

# Copy .env for Windows (PowerShell)
copy-env-windows:
	@powershell -Command "if (-Not (Test-Path 'docker.env')) {Copy-Item 'example.env' 'docker.env'; Write-Host 'Copied example.env to docker.env.'} else {Write-Host 'docker.env already exists.'}"

# Copy .env for Linux/Ubuntu (bash)
copy-env-linux:
	@if [ ! -f docker.env ]; then \
		cp example.env docker.env && echo "Copied example.env to docker.env."; \
	else \
		echo "docker.env already exists."; \
	fi
# Build the web, daphne, and nginx containers
build:
	$(DOCKER_COMPOSE) build

# Run makemigrations
migrations:
	$(DOCKER_COMPOSE) run --rm web python manage.py makemigrations

# Apply migrations
migrate:
	$(DOCKER_COMPOSE) run --rm web python manage.py migrate

# Start the development server (use docker-compose.yml)
up:
	$(DOCKER_COMPOSE) up

# Stop and remove containers, networks, and volumes
down:
	$(DOCKER_COMPOSE) down

# View logs of running services
logs:
	$(DOCKER_COMPOSE) logs -f

# Run tests
test:
	$(DOCKER_COMPOSE) run --rm web python manage.py test

# Create superuser
createsuperuser:
	$(DOCKER_COMPOSE) run --rm web python manage.py createsuperuser

# Clear volumes (be cautious)
clear-volumes:
	$(DOCKER_COMPOSE) down -v

# Build and run everything (all-in-one shortcut)
start:
	make build
	make up

# Load fixtures
load-fixtures:
	$(DOCKER_COMPOSE) run --rm web python manage.py loaddata general_fixture.json
# start stripe webhook
stripe-webhook:
	@stripe listen --forward-to $(STRIPE_WEBHOOK_URL)

