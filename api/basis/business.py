"""Company, trust, dividends, donations, VAT, turnover tax, transfer duty and UIF."""

from __future__ import annotations

from typing import Literal

from .core import Trace, progressive_tax, rands
from .tables import CONFIG


def company_tax(*, taxable_income: float, config: dict = CONFIG) -> dict:
    rate = config["company_tax_rate"]
    t = Trace()
    t.add("Company taxable income", taxable_income)
    tax = max(0.0, taxable_income) * rate
    t.add("Company income tax", tax, f"flat {rate:.0%}")
    return {"tax_year": config["year"], "tax": rands(tax), "rate": rate,
            "after_tax": rands(taxable_income - tax), "steps": t.steps}


def trust_tax(*, taxable_income: float, config: dict = CONFIG) -> dict:
    rate = config["trust_tax_rate"]
    t = Trace()
    t.add("Trust taxable income", taxable_income)
    tax = max(0.0, taxable_income) * rate
    t.add("Trust income tax", tax, f"flat {rate:.0%} (non-special trust)")
    return {"tax_year": config["year"], "tax": rands(tax), "rate": rate,
            "after_tax": rands(taxable_income - tax), "steps": t.steps}


def dividends_tax(*, dividend: float, config: dict = CONFIG) -> dict:
    rate = config["dividends_tax_rate"]
    t = Trace()
    t.add("Dividend declared", dividend)
    tax = max(0.0, dividend) * rate
    t.add("Dividends withholding tax", tax, f"{rate:.0%}, withheld by the company")
    t.add("Net dividend received", dividend - tax)
    return {"tax_year": config["year"], "tax": rands(tax), "rate": rate,
            "net_dividend": rands(dividend - tax), "steps": t.steps}


def donations_tax(*, amount: float, cumulative_prior: float = 0.0, config: dict = CONFIG) -> dict:
    d = config["donations_tax"]
    t = Trace()
    t.add("Donation", amount)
    exemption = min(amount, d["annual_exemption"])
    t.add("Less annual exemption", -exemption, f"R{d['annual_exemption']:,.0f} per year")
    taxable = max(0.0, amount - exemption)
    total_after = cumulative_prior + taxable
    if total_after <= d["excess_threshold"]:
        tax = taxable * d["standard_rate"]
        t.add("Donations tax", tax, f"{d['standard_rate']:.0%}")
    else:
        below = max(0.0, d["excess_threshold"] - cumulative_prior)
        at_standard = min(taxable, below)
        at_excess = taxable - at_standard
        tax = at_standard * d["standard_rate"] + at_excess * d["excess_rate"]
        t.add("Donations tax", tax, f"{d['standard_rate']:.0%} up to R30m cumulative, then {d['excess_rate']:.0%}")
    return {"tax_year": config["year"], "taxable_donation": rands(taxable),
            "tax": rands(tax), "steps": t.steps}


def vat(*, amount: float, direction: Literal["add", "extract"] = "add", config: dict = CONFIG) -> dict:
    rate = config["vat_rate"]
    t = Trace()
    if direction == "add":
        t.add("Amount excluding VAT", amount)
        v = amount * rate
        t.add("VAT", v, f"{rate:.0%}")
        t.add("Amount including VAT", amount + v)
        return {"tax_year": config["year"], "vat": rands(v), "excl": rands(amount),
                "incl": rands(amount + v), "rate": rate, "steps": t.steps}
    t.add("Amount including VAT", amount)
    excl = amount / (1 + rate)
    v = amount - excl
    t.add("VAT portion", v, f"amount x {rate:.0f}/{100 + rate * 100:.0f}")
    t.add("Amount excluding VAT", excl)
    return {"tax_year": config["year"], "vat": rands(v), "excl": rands(excl),
            "incl": rands(amount), "rate": rate, "steps": t.steps}


def turnover_tax(*, turnover: float, config: dict = CONFIG) -> dict:
    t = Trace()
    t.add("Annual turnover", turnover)
    if turnover > config["turnover_tax_max_turnover"]:
        t.add("Not eligible", None,
              f"turnover tax only applies up to R{config['turnover_tax_max_turnover']:,.0f}")
    tax, br = progressive_tax(turnover, config["turnover_tax_brackets"])
    t.add("Turnover tax", tax, f"R{br[2]:,.0f} + {br[3]:.0%} of turnover above R{br[0]:,.0f}")
    return {"tax_year": config["year"], "tax": rands(tax),
            "eligible": turnover <= config["turnover_tax_max_turnover"],
            "effective_rate": round(tax / turnover, 4) if turnover > 0 else 0.0, "steps": t.steps}


def transfer_duty(*, property_value: float, config: dict = CONFIG) -> dict:
    t = Trace()
    t.add("Property value", property_value)
    duty, br = progressive_tax(property_value, config["transfer_duty_brackets"])
    free = config["transfer_duty_brackets"][1][0]
    t.add("Duty-free threshold", 0.0, f"no duty up to R{free:,.0f}")
    t.add("Transfer duty", duty, f"R{br[2]:,.0f} + {br[3]:.0%} of value above R{br[0]:,.0f}")
    return {"tax_year": config["year"], "duty": rands(duty),
            "effective_rate": round(duty / property_value, 4) if property_value > 0 else 0.0,
            "steps": t.steps}


def uif(*, monthly_remuneration: float, config: dict = CONFIG) -> dict:
    u = config["uif"]
    t = Trace()
    t.add("Monthly remuneration", monthly_remuneration)
    base = min(monthly_remuneration, u["monthly_ceiling"])
    t.add("Capped remuneration", base, f"ceiling R{u['monthly_ceiling']:,.2f}")
    employee = base * u["rate"]
    t.add("Employee contribution", employee, f"{u['rate']:.0%}")
    t.add("Employer contribution", employee, f"{u['rate']:.0%}")
    return {"tax_year": config["year"], "employee": rands(employee), "employer": rands(employee),
            "total": rands(employee * 2), "steps": t.steps}
