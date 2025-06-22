.PHONY: help install dev build test clean

help:
	@echo "Commandes disponibles:"
	@echo "  make install    - Installe les dépendances"
	@echo "  make dev       - Lance l'environnement de développement"
	@echo "  make build     - Build les images Docker"
	@echo "  make test      - Lance les tests"
	@echo "  make clean     - Nettoie les fichiers temporaires"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	docker-compose up -d postgres redis
	cd backend && uvicorn main:app --reload &
	cd frontend && npm run dev &
	cd ml-pipeline/comfyui && python start_server.py

build:
	docker-compose build

test:
	cd backend && pytest
	cd frontend && npm test

migrate:
	cd backend && alembic upgrade head

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf frontend/.next
	rm -rf frontend/node_modules
