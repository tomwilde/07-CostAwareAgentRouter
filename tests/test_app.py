from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def test_required_tasks_visible_in_ui() -> None:
    at = AppTest.from_file(APP_PATH).run()

    labels = [option for option in at.selectbox[0].options]
    assert "Generating a poem about Capital vs Labour" in labels
    assert "Sentiment detection on a sample paragraph of text" in labels


def test_run_generates_decision_report(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        "src.router._live_openrouter_output",
        lambda task_id, api_key, model_name: f"mocked-{task_id}-{model_name}",
    )

    at = AppTest.from_file(APP_PATH)
    at.session_state["token_budget"] = 500
    at.session_state["confidence_threshold"] = 0.85
    at = at.run()

    at.button(key="run_task").click().run()

    assert any("Model Selected" in item.value for item in at.markdown)
    assert any("Cost per Decision" in item.value for item in at.markdown)


def test_missing_key_error_in_live_mode(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    at = AppTest.from_file(APP_PATH)
    at = at.run()

    at.button(key="run_task").click().run()

    assert any("OPENROUTER_API_KEY" in alert.value for alert in at.error)

