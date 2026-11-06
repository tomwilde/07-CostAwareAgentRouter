from __future__ import annotations

import os
from dataclasses import dataclass

TASK_LABELS: dict[str, str] = {
    "poem": "Generating a poem about Capital vs Labour",
    "sentiment": "Sentiment detection on a sample paragraph of text",
}

TASK_COMPLEXITY: dict[str, float] = {
    "poem": 0.82,
    "sentiment": 0.35,
}

TASK_ESTIMATED_TOKENS: dict[str, int] = {
    "poem": 420,
    "sentiment": 180,
}


@dataclass(frozen=True)
class ModelOption:
    name: str
    capability: float
    cost_per_1k_tokens_usd: float


@dataclass(frozen=True)
class DecisionReport:
    token_budget: int
    tokens_consumed: int
    within_budget: bool
    model_selected: str
    routing_rationale: str
    early_exit: bool
    confidence: float
    cost_per_decision_usd: float


@dataclass(frozen=True)
class TaskResult:
    output: str
    report: DecisionReport


MODEL_OPTIONS: tuple[ModelOption, ...] = (
    ModelOption(name="openai/gpt-4.1-mini", capability=0.55, cost_per_1k_tokens_usd=0.20),
    ModelOption(name="openai/gpt-5.4", capability=0.95, cost_per_1k_tokens_usd=2.00),
)


def run_task(
    task_id: str,
    token_budget: int,
    confidence_threshold: float,
    openrouter_api_key: str | None = None,
) -> TaskResult:
    if task_id not in TASK_LABELS:
        raise ValueError(f"Unsupported task: {task_id}")

    effective_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
    if not effective_key:
        return _build_result(
            output=(
                "Missing OPENROUTER_API_KEY. Set it in your local environment "
                "to run live OpenRouter calls."
            ),
            token_budget=token_budget,
            tokens_consumed=0,
            model=MODEL_OPTIONS[1],
            early_exit=False,
            confidence=0.0,
            rationale="Live OpenRouter call required but key was not available.",
        )

    estimated_tokens = TASK_ESTIMATED_TOKENS[task_id]
    if estimated_tokens > token_budget:
        return _budget_exceeded_result(task_id=task_id, token_budget=token_budget)

    base_confidence = _cheap_model_confidence(task_id)
    complexity = TASK_COMPLEXITY[task_id]
    low_cost_model = MODEL_OPTIONS[0]

    if base_confidence >= confidence_threshold and complexity <= low_cost_model.capability:
        output = _live_openrouter_output(
            task_id=task_id,
            api_key=effective_key,
            model_name=low_cost_model.name,
        )
        return _build_result(
            output=output,
            token_budget=token_budget,
            tokens_consumed=estimated_tokens,
            model=low_cost_model,
            early_exit=True,
            confidence=base_confidence,
            rationale="Low complexity task reached confidence threshold on low-cost model.",
        )

    selected_model = MODEL_OPTIONS[1]
    output = _live_openrouter_output(
        task_id=task_id,
        api_key=effective_key,
        model_name=selected_model.name,
    )

    return _build_result(
        output=output,
        token_budget=token_budget,
        tokens_consumed=estimated_tokens,
        model=selected_model,
        early_exit=False,
        confidence=max(base_confidence, 0.91),
        rationale="Escalated to higher-capability model for quality under constraints.",
    )


def _build_result(
    output: str,
    token_budget: int,
    tokens_consumed: int,
    model: ModelOption,
    early_exit: bool,
    confidence: float,
    rationale: str,
) -> TaskResult:
    cost = round((tokens_consumed / 1000) * model.cost_per_1k_tokens_usd, 6)
    report = DecisionReport(
        token_budget=token_budget,
        tokens_consumed=tokens_consumed,
        within_budget=tokens_consumed <= token_budget,
        model_selected=model.name,
        routing_rationale=rationale,
        early_exit=early_exit,
        confidence=round(confidence, 3),
        cost_per_decision_usd=cost,
    )
    return TaskResult(output=output, report=report)


def _budget_exceeded_result(task_id: str, token_budget: int) -> TaskResult:
    report = DecisionReport(
        token_budget=token_budget,
        tokens_consumed=0,
        within_budget=False,
        model_selected=MODEL_OPTIONS[0].name,
        routing_rationale="Execution skipped due to token budget guardrail.",
        early_exit=False,
        confidence=0.0,
        cost_per_decision_usd=0.0,
    )
    return TaskResult(
        output=(
            f"Task '{TASK_LABELS[task_id]}' was not executed because the configured "
            "token budget is too low."
        ),
        report=report,
    )


def _cheap_model_confidence(task_id: str) -> float:
    if task_id == "sentiment":
        return 0.93
    return 0.67


def _live_openrouter_output(task_id: str, api_key: str, model_name: str) -> str:
    from openai import OpenAI

    prompts = {
        "poem": "Write a short poem about Capital and Labour in four lines.",
        "sentiment": (
            "Classify sentiment of this sentence as positive/neutral/negative: "
            "The release missed deadlines but the team handled issues responsibly."
        ),
    }
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompts[task_id]}],
        temperature=0.2,
    )
    content = completion.choices[0].message.content
    return content or "No response content returned by model."

