import os

import streamlit as st

from src.router import TASK_LABELS, run_task

st.set_page_config(page_title="Cost-Aware Agent Router", page_icon="🧭")
st.title("Cost-Aware Agent Router")

task_options = {label: task_id for task_id, label in TASK_LABELS.items()}

selected_label = st.selectbox(
    "Choose a task",
    options=list(task_options.keys()),
    key="task_selector",
)

st.number_input("Token budget", min_value=1, value=500, step=50, key="token_budget")
st.slider(
    "Confidence threshold",
    min_value=0.5,
    max_value=0.99,
    value=0.85,
    step=0.01,
    key="confidence_threshold",
)

if st.button("Run task", key="run_task"):
    task_id = task_options[selected_label]
    result = run_task(
        task_id=task_id,
        token_budget=int(st.session_state.token_budget),
        confidence_threshold=float(st.session_state.confidence_threshold),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    st.markdown("### Task Output")
    st.write(result.output)

    if "OPENROUTER_API_KEY" in result.output:
        st.error(result.output)

    st.markdown("### Decision Report")
    st.markdown(f"- **Token Budget**: `{result.report.token_budget}`")
    st.markdown(f"- **Tokens Consumed**: `{result.report.tokens_consumed}`")
    st.markdown(f"- **Within Budget**: `{result.report.within_budget}`")
    st.markdown(f"- **Model Selected**: `{result.report.model_selected}`")
    st.markdown(f"- **Routing Rationale**: {result.report.routing_rationale}")
    st.markdown(f"- **Early Exit**: `{result.report.early_exit}`")
    st.markdown(f"- **Confidence**: `{result.report.confidence}`")
    st.markdown(
        "- **Cost per Decision**: "
        f"`${result.report.cost_per_decision_usd:.6f}`"
    )

