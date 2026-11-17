"""SA Tax Hub engine (2026/2027). Pure-Python tax calculations with explanations."""

from .business import (
    company_tax, dividends_tax, donations_tax, transfer_duty, trust_tax,
    turnover_tax, uif, vat,
)
from .capital_gains import capital_gains_tax
from .core import bracket_rows
from .income import income_tax, provisional_tax
from .retirement import lump_sum_tax, retirement_deduction
from .tables import CONFIG

__all__ = [
    "income_tax", "provisional_tax", "capital_gains_tax", "lump_sum_tax",
    "retirement_deduction", "company_tax", "trust_tax", "dividends_tax",
    "donations_tax", "vat", "turnover_tax", "transfer_duty", "uif",
    "bracket_rows", "CONFIG",
]
