# Variables
DOCKER_COMPOSE=docker-compose
PROJECT_NAME=core
STRIPE_WEBHOOK_URL=http://localhost:8000/stripe/webhook/

# Default target: run initial setup
initial: copy-env build migrations migrate up

# Copy .env.example to docker.env (Windows-friendly with PowerShell)
copy-env:
	@powershell -Command "if (-Not (Test-Path 'docker.env')) {Copy-Item '.env.example' 'docker.env'; Write-Host 'Copied .env.example to docker.env.'} else {Write-Host 'docker.env already exists.'}"

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

