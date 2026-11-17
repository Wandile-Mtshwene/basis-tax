"""Retirement fund lump sum and withdrawal tax (SARS once-off tables).

Both tables are cumulative: tax is worked out on all lump sums taken to date,
less the tax on prior lump sums. This hub applies the table to a single benefit
for clarity (the common quote), and notes the aggregation rule.
"""

from __future__ import annotations

from typing import Literal

from .core import Trace, progressive_tax, rands
from .tables import CONFIG

Kind = Literal["retirement", "withdrawal"]


def lump_sum_tax(*, amount: float, kind: Kind = "retirement", config: dict = CONFIG) -> dict:
    brackets = (config["retirement_lump_sum_brackets"] if kind == "retirement"
                else config["withdrawal_brackets"])
    t = Trace()
    label = "retirement or death benefit" if kind == "retirement" else "pre-retirement withdrawal (incl. two-pot)"
    t.add("Lump sum amount", amount, label)
    tax, br = progressive_tax(amount, brackets)
    free = brackets[1][0] if len(brackets) > 1 else 0
    t.add(f"Tax-free portion", 0.0, f"first R{free:,.0f} is taxed at 0%")
    t.add("Tax on the lump sum", tax, f"R{br[2]:,.0f} + {br[3]:.0%} of amount above R{br[0]:,.0f}")
    net = amount - tax
    t.add("Net lump sum received", net)
    return {
        "tax_year": config["year"],
        "kind": kind,
        "lump_sum": rands(amount),
        "tax": rands(tax),
        "net": rands(net),
        "effective_rate": round(tax / amount, 4) if amount > 0 else 0.0,
        "note": "Tables are cumulative across all lump sums taken to date; this applies the table to a single benefit.",
        "steps": t.steps,
    }


def retirement_deduction(*, income: float, contribution: float, config: dict = CONFIG) -> dict:
    """The deductible portion of a retirement-fund contribution."""
    rc = config["retirement_contribution"]
    t = Trace()
    t.add("Retirement contribution", contribution)
    pct_cap = rc["max_percent"] * income
    deductible = min(contribution, pct_cap, rc["annual_cap"])
    t.add(f"{rc['max_percent']:.1%} of income", pct_cap)
    t.add("Annual cap", rc["annual_cap"])
    t.add("Deductible amount", deductible, "the lowest of the three")
    disallowed = contribution - deductible
    if disallowed > 0:
        t.add("Carried forward to next year", disallowed)
    return {
        "tax_year": config["year"],
        "deductible": rands(deductible),
        "carried_forward": rands(max(0.0, disallowed)),
        "steps": t.steps,
    }
