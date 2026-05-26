.PHONY: help build dev test lint clean up down logs

IMAGE_NAME=safeprompt-api
VERSION?=latest

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build production Docker image
	docker build -t $(IMAGE_NAME):$(VERSION) ./app

dev: ## Start development environment with hot reload
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

up: ## Start production stack
	docker compose up -d --build
	@echo "SafePrompt running at http://localhost"

down: ## Stop all services
	docker compose down

logs: ## Tail logs from all services
	docker compose logs -f

test: ## Run tests inside Docker
	docker run --rm \
		-v $(PWD)/tests:/tests \
		-v $(PWD)/app:/app \
		-w /app \
		$(IMAGE_NAME):$(VERSION) \
		sh -c "pip install pytest pytest-asyncio httpx && pytest /tests -v"

lint: ## Run linter
	docker run --rm -v $(PWD)/app:/app -w /app python:3.12-slim \
		sh -c "pip install ruff && ruff check ."

scan: ## Scan image for vulnerabilities with Trivy
	trivy image $(IMAGE_NAME):$(VERSION)

clean: ## Remove containers, images, volumes
	docker compose down -v --rmi local
	docker rmi $(IMAGE_NAME):$(VERSION) 2>/dev/null || true

push: ## Push image to registry (set REGISTRY env var)
	docker tag $(IMAGE_NAME):$(VERSION) $(REGISTRY)/$(IMAGE_NAME):$(VERSION)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(VERSION)
