.PHONY: test-backend lint-backend format-backend run-backend typecheck-backend test-frontend lint-frontend format-frontend 

# Backend
test-backend:
	cd backend && .venv/bin/pytest

test-backend-file:
	cd backend && .venv/bin/pytest tests/$(FILE)

lint-backend:
	cd backend && .venv/bin/ruff check src

format-backend:
	cd backend && .venv/bin/ruff format src

run-backend:
	cd backend && .venv/bin/uvicorn regatta.main:app --reload

typecheck-backend:
	cd backend && .venv/bin/pyright src

# Frontend
test-frontend:
	cd frontend && npm test

lint-frontend:
	cd frontend && npm run lint

format-frontend:
	cd frontend && npm run format
