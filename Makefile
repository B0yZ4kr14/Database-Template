# Database Makefile
# =================

.PHONY: help install dev build test clean docker

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instala o sistema"
	@echo "  make dev           - Inicia em modo desenvolvimento"
	@echo "  make build         - Build do frontend"
	@echo "  make test          - Executa testes"
	@echo "  make clean         - Limpa arquivos temporários"
	@echo "  make docker-up     - Inicia containers Docker"
	@echo "  make docker-down   - Para containers Docker"

install:
	sudo bash scripts/install.sh

dev-backend:
	cd backend && source venv/bin/activate && python main.py

dev-frontend:
	cd frontend && npm run dev

build:
	cd frontend && npm install && npm run build

test:
	cd backend && source venv/bin/activate && pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/dist frontend/node_modules

docker-up:
	cd docker && docker-compose up -d

docker-down:
	cd docker && docker-compose down
