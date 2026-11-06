from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.acceptance
def test_end_to_end_router_flow_and_report(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        "src.router._live_openrouter_output",
        lambda task_id, api_key, model_name: f"mocked-{task_id}-{model_name}",
    )

    at = AppTest.from_file(APP_PATH)
    at.session_state["token_budget"] = 650
    at.session_state["confidence_threshold"] = 0.9
    at = at.run()

    at.selectbox(key="task_selector").select(
        "Generating a poem about Capital vs Labour"
    ).run()
    at.button(key="run_task").click().run()

    assert any("Task Output" in item.value for item in at.markdown)
    assert any("Routing Rationale" in item.value for item in at.markdown)
    assert any("openai/gpt-5.4" in item.value for item in at.markdown)

