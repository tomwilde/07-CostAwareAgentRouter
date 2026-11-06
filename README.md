# Cost-Aware Agent Router

Streamlit app that demonstrates task-based token budgeting, model routing by cost/complexity, early exit on confidence, and cost-per-decision reporting.

## Objective and Acceptance

- Objective: [`objective.md`](objective.md)
- Acceptance tests spec: [`acceptance-tests.md`](acceptance-tests.md)

## Prerequisites

- Python 3.12+
- `uv` installed
- Docker + Docker Compose (for containerized runtime)

## Local Setup

```bash
make install
```

## Run Tests

```bash
make test
make acceptance
```

## Run App Locally

```bash
uv run streamlit run app.py
```

## OpenRouter Live LLM

Supports model `openai/gpt-4.1-mini` via OpenRouter. Use local env var only:

```bash
export OPENROUTER_API_KEY="..."
```

All task executions use live OpenRouter calls (no offline toggle).

Do not commit secrets to the repository.

## Docker Profiles

Only run one profile at a time (both use port `8501`).

- App mode (normal runtime):

  ```bash
  make app
  ```

- Debug mode (VS Code attach + live edits):

  ```bash
  make debug
  ```

## VS Code Debug Attach

1. Start debug profile with `make debug`.
2. In VS Code, run `Attach: Cost-Aware Router (Docker Debug)` from `.vscode/launch.json`.

