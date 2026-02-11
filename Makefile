.PHONY: setup dev dev-server dev-client test format migrate db-up db-down

# ─── Setup ───
setup: db-up
	cd server && uv sync
	cd client && pnpm install

# ─── Development ───
dev:
	$(MAKE) dev-server & $(MAKE) dev-client & wait

dev-server:
	cd server && uv run uvicorn chesslens.main:app --reload --port 8000

dev-client:
	cd client && pnpm dev

# ─── Database ───
db-up:
	docker compose up -d

db-down:
	docker compose down

migrate:
	cd server && uv run alembic upgrade head

migrate-new:
	cd server && uv run alembic revision --autogenerate -m "$(MSG)"

# ─── Testing ───
test:
	cd server && uv run pytest
	cd client && pnpm test

test-server:
	cd server && uv run pytest

test-client:
	cd client && pnpm test

# ─── Formatting ───
format:
	cd server && uv run ruff check --fix . && uv run ruff format .
	cd client && pnpm biome check --write .

lint:
	cd server && uv run ruff check .
	cd client && pnpm biome check .

# ─── CLI ───
fetch:
	cd server && uv run chesslens fetch $(USER)

analyze:
	cd server && uv run chesslens analyze $(GAME_ID)
