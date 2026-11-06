.PHONY: install test acceptance lint type qa app debug down

install:
	uv sync

test:
	uv run pytest tests/ -v

acceptance:
	uv run pytest -m acceptance -v

lint:
	uv run ruff check .

type:
	uv run ty check

qa: test acceptance lint type

app:
	docker compose --profile app down
	docker compose --profile app up --build

debug:
	docker compose --profile debug down
	docker compose --profile debug up --build

down:
	docker compose --profile app --profile debug down

