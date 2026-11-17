"""Capital gains tax."""

from __future__ import annotations

from typing import Literal

from .core import Trace, rands
from .tables import CONFIG

Taxpayer = Literal["individual", "company", "trust"]


def capital_gains_tax(
    *, proceeds: float, base_cost: float, taxpayer: Taxpayer = "individual",
    marginal_rate: float = 0.45, is_primary_residence: bool = False,
    annual_exclusion_available: bool = True, config: dict = CONFIG,
) -> dict:
    cfg = config["cgt"]
    t = Trace()

    gain = proceeds - base_cost
    t.add("Proceeds", proceeds)
    t.add("Less base cost", -base_cost)
    t.add("Capital gain", gain)

    if gain <= 0:
        t.add("No capital gain", 0.0, "a capital loss carries forward")
        return {"tax_year": config["year"], "capital_gain": rands(gain), "taxable_gain": 0.0,
                "cgt": 0.0, "effective_rate": 0.0, "steps": t.steps}

    if is_primary_residence and taxpayer == "individual":
        excl = min(gain, cfg["primary_residence_exclusion"])
        gain -= excl
        t.add("Less primary residence exclusion", -excl, f"up to R{cfg['primary_residence_exclusion']:,.0f}")

    if taxpayer == "individual" and annual_exclusion_available:
        excl = min(gain, cfg["annual_exclusion"])
        gain = max(0.0, gain - excl)
        t.add("Less annual exclusion", -excl, f"R{cfg['annual_exclusion']:,.0f}")

    inclusion = (cfg["individual_inclusion_rate"] if taxpayer == "individual"
                 else cfg["company_inclusion_rate"] if taxpayer == "company"
                 else cfg["trust_inclusion_rate"])
    taxable_gain = gain * inclusion
    t.add("Taxable gain included in income", taxable_gain, f"{inclusion:.0%} inclusion rate")

    rate = (marginal_rate if taxpayer == "individual"
            else config["company_tax_rate"] if taxpayer == "company"
            else config["trust_tax_rate"])
    tax = taxable_gain * rate
    t.add("Capital gains tax", tax, f"taxed at {rate:.0%}")

    original_gain = proceeds - base_cost
    return {
        "tax_year": config["year"],
        "capital_gain": rands(original_gain),
        "inclusion_rate": inclusion,
        "taxable_gain": rands(taxable_gain),
        "cgt": rands(tax),
        "effective_rate": round(tax / original_gain, 4) if original_gain > 0 else 0.0,
        "steps": t.steps,
    }
