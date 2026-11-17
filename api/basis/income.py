"""Personal income tax and PAYE."""

from __future__ import annotations

from .core import Trace, marginal_rate, progressive_tax, rands
from .tables import CONFIG


def medical_tax_credit_annual(members: int, config: dict = CONFIG) -> float:
    """Annual medical scheme fees tax credit for a given number of people covered."""
    if members <= 0:
        return 0.0
    mc = config["medical_credits"]
    monthly = mc["main_member"]
    if members >= 2:
        monthly += mc["first_dependant"]
    if members > 2:
        monthly += (members - 2) * mc["additional_dependant"]
    return monthly * 12


def total_rebate(age: int, config: dict = CONFIG) -> tuple[float, list[str]]:
    r = config["rebates"]
    total, names = r["primary"], ["primary"]
    if age >= 65:
        total += r["secondary_65"]; names.append("secondary (65+)")
    if age >= 75:
        total += r["tertiary_75"]; names.append("tertiary (75+)")
    return total, names


def income_tax(
    *, annual_income: float, age: int = 40, medical_members: int = 0,
    retirement_contribution: float = 0.0, config: dict = CONFIG,
) -> dict:
    t = Trace()
    t.add("Gross annual income", annual_income)

    rc = config["retirement_contribution"]
    deductible = min(retirement_contribution, rc["max_percent"] * annual_income, rc["annual_cap"])
    if retirement_contribution > 0:
        t.add("Less deductible retirement contribution", -deductible,
              f"capped at {rc['max_percent']:.1%} of income or R{rc['annual_cap']:,.0f}")
    taxable = max(0.0, annual_income - deductible)
    t.add("Taxable income", taxable)

    tax_before, br = progressive_tax(taxable, config["individual_brackets"])
    t.add("Tax on the sliding scale", tax_before,
          f"R{br[2]:,.0f} + {br[3]:.0%} of income above R{br[0]:,.0f}")

    rebate, names = total_rebate(age, config)
    t.add("Less tax rebates", -rebate, " + ".join(names))
    after_rebates = max(0.0, tax_before - rebate)
    t.add("Tax after rebates", after_rebates)

    mtc = medical_tax_credit_annual(medical_members, config)
    if mtc > 0:
        t.add("Less medical scheme tax credits", -mtc,
              f"{medical_members} person(s) covered, annualised")
    net = max(0.0, after_rebates - mtc)
    t.add("Annual tax payable", net)
    t.add("Monthly PAYE", net / 12)

    thresholds = config["tax_thresholds"]
    threshold = (thresholds["age_75_plus"] if age >= 75
                 else thresholds["age_65_to_74"] if age >= 65
                 else thresholds["under_65"])

    return {
        "tax_year": config["year"],
        "taxable_income": rands(taxable),
        "tax_before_rebates": rands(tax_before),
        "rebates": rands(rebate),
        "medical_credits": rands(mtc),
        "annual_tax": rands(net),
        "monthly_paye": rands(net / 12),
        "net_annual_income": rands(annual_income - net),
        "effective_rate": round(net / annual_income, 4) if annual_income > 0 else 0.0,
        "marginal_rate": marginal_rate(taxable, config["individual_brackets"]),
        "tax_threshold": threshold,
        "below_threshold": net <= 0,
        "steps": t.steps,
    }


def provisional_tax(
    *, estimated_taxable_income: float, age: int = 40, already_paid: float = 0.0,
    config: dict = CONFIG,
) -> dict:
    """First/second provisional payment: tax on estimated income, split over the year."""
    base = income_tax(annual_income=estimated_taxable_income, age=age, config=config)
    liability = base["annual_tax"]
    t = Trace()
    t.add("Estimated annual tax", liability)
    first = liability / 2
    t.add("First payment (end of month 6)", first, "half of the estimated liability")
    second = max(0.0, liability - first - already_paid)
    t.add("Second payment (end of month 12)", second, "balance of the liability")
    return {
        "tax_year": config["year"],
        "estimated_annual_tax": liability,
        "first_payment": rands(first),
        "second_payment": rands(second),
        "steps": t.steps,
    }
