.PHONY: dev test test-integration lint up down logs build-frontend

dev:
	docker compose up --build

test:
	cd backend && pytest
	cd frontend && npm test

test-integration:
	powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/test-backend.ps1

build-frontend:
	cd frontend && npm.cmd run build

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

up:
	docker compose up -d --build --force-recreate

down:
	docker compose down

logs:
	docker compose logs -f
