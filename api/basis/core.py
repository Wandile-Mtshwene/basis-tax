"""Shared helpers: progressive-bracket tax and the explanation-trace builder.

Every calculator returns a plain dict with a ``steps`` list so the UI can show
exactly how a number was reached, line by line.
"""

from __future__ import annotations

Bracket = tuple  # (lower, upper_or_None, base_tax, rate)


def progressive_tax(amount: float, brackets: list[Bracket]) -> tuple[float, Bracket]:
    """Tax from a cumulative-base bracket table. Returns (tax, bracket_used)."""
    if amount <= 0:
        return 0.0, brackets[0]
    for b in brackets:
        lower, upper, base, rate = b
        if amount > lower and (upper is None or amount <= upper):
            return base + rate * (amount - lower), b
    last = brackets[-1]
    lower, _, base, rate = last
    return base + rate * (amount - lower), last


def marginal_rate(amount: float, brackets: list[Bracket]) -> float:
    for lower, upper, _base, rate in brackets:
        if amount > lower and (upper is None or amount <= upper):
            return rate
    return brackets[-1][3]


def rands(x: float) -> float:
    return round(float(x), 2)


class Trace:
    """Accumulates human-readable calculation steps."""

    def __init__(self) -> None:
        self._steps: list[dict] = []

    def add(self, label: str, amount: float | None = None, note: str = "") -> None:
        self._steps.append({
            "label": label,
            "amount": None if amount is None else rands(amount),
            "note": note,
        })

    @property
    def steps(self) -> list[dict]:
        return self._steps


def bracket_rows(brackets: list[Bracket]) -> list[dict]:
    """Render a bracket table for display."""
    rows = []
    for lower, upper, base, rate in brackets:
        rows.append({
            "from": lower,
            "to": upper,
            "base_tax": base,
            "rate": rate,
        })
    return rows
