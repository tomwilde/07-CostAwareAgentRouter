from src.router import run_task


def test_sentiment_prefers_low_cost_model_with_early_exit(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        "src.router._live_openrouter_output",
        lambda task_id, api_key, model_name: f"mocked-{task_id}-{model_name}",
    )

    result = run_task(task_id="sentiment", token_budget=300, confidence_threshold=0.85)

    assert result.report.model_selected == "openai/gpt-4.1-mini"
    assert result.report.early_exit is True
    assert result.report.tokens_consumed <= 300


def test_poem_routes_to_more_capable_model_when_needed(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        "src.router._live_openrouter_output",
        lambda task_id, api_key, model_name: f"mocked-{task_id}-{model_name}",
    )

    result = run_task(task_id="poem", token_budget=600, confidence_threshold=0.9)

    assert result.report.model_selected == "openai/gpt-5.4"
    assert result.report.early_exit is False
    assert "mocked-poem-openai/gpt-5.4" in result.output


def test_budget_exceeded_short_circuits_execution() -> None:
    result = run_task(task_id="poem", token_budget=50, confidence_threshold=0.8)

    assert result.report.within_budget is False
    assert result.report.tokens_consumed == 0
    assert "budget" in result.output.lower()


def test_missing_openrouter_key_returns_clear_error(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    result = run_task(
        task_id="poem",
        token_budget=600,
        confidence_threshold=0.5,
        openrouter_api_key=None,
    )

    assert "OPENROUTER_API_KEY" in result.output

