.PHONY: dev test lint format db-up db-down

# Start Postgres, then run the API with auto-reload
dev: db-up
	uv run uvicorn app.main:app --reload

test:
	uv run pytest

# Runs both checks even if the first fails, then fails overall
lint:
	uv run ruff check . ; r=$$? ; \
	uv run mypy . ; m=$$? ; \
	exit $$((r + m))

format:
	uv run ruff format .

db-up:
	docker compose up -d db

db-down:
	docker compose down
