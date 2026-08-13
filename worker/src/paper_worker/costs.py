from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPrice:
    input_per_million: float
    output_per_million: float


MODEL_PRICES = {
    "gpt-5.6-sol": ModelPrice(5.0, 30.0),
    "gpt-5.6-terra": ModelPrice(2.5, 15.0),
    "gpt-5.6-luna": ModelPrice(1.0, 6.0),
}


def estimate_text_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price = MODEL_PRICES.get(model)
    if not price:
        return 0.0
    return (
        input_tokens * price.input_per_million + output_tokens * price.output_per_million
    ) / 1_000_000


class BudgetExceeded(RuntimeError):
    pass
