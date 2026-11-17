"""SA Tax Hub - FastAPI service.

A calculation and explanation hub for South African taxes (2026/2027). Every
endpoint returns the result plus a step-by-step trace of how it was reached.
Not payroll, not advice.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import basis
from basis.tables import CONFIG

app = FastAPI(
    title="SA Tax Hub", version="1.0.0",
    docs_url="/api/docs", openapi_url="/api/openapi.json",
    description="South African tax calculations for 2026/2027, each explained step by step.",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
router = APIRouter(prefix="/api")


@router.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "service": "basis-tax", "tax_year": CONFIG["year"]}


# ------------------------------- requests ---------------------------------- #
class IncomeReq(BaseModel):
    annual_income: float = Field(600_000, ge=0)
    age: int = Field(40, ge=0, le=120)
    medical_members: int = Field(0, ge=0, le=20)
    retirement_contribution: float = Field(0, ge=0)


class ProvisionalReq(BaseModel):
    estimated_taxable_income: float = Field(600_000, ge=0)
    age: int = Field(40, ge=0, le=120)
    already_paid: float = Field(0, ge=0)


class CGTReq(BaseModel):
    proceeds: float = Field(2_000_000, ge=0)
    base_cost: float = Field(1_000_000, ge=0)
    taxpayer: Literal["individual", "company", "trust"] = "individual"
    marginal_rate: float = Field(0.45, ge=0, le=0.45)
    is_primary_residence: bool = False
    annual_exclusion_available: bool = True


class LumpSumReq(BaseModel):
    amount: float = Field(900_000, ge=0)
    kind: Literal["retirement", "withdrawal"] = "retirement"


class RetDeductionReq(BaseModel):
    income: float = Field(600_000, ge=0)
    contribution: float = Field(150_000, ge=0)


class AmountReq(BaseModel):
    amount: float = Field(1_000_000, ge=0)


class DonationReq(BaseModel):
    amount: float = Field(250_000, ge=0)
    cumulative_prior: float = Field(0, ge=0)


class VatReq(BaseModel):
    amount: float = Field(1_000, ge=0)
    direction: Literal["add", "extract"] = "add"


class TurnoverReq(BaseModel):
    turnover: float = Field(900_000, ge=0)


class PropertyReq(BaseModel):
    property_value: float = Field(2_000_000, ge=0)


class UifReq(BaseModel):
    monthly_remuneration: float = Field(25_000, ge=0)


# ------------------------------- endpoints --------------------------------- #
@router.post("/tax/income", tags=["personal"])
def income(req: IncomeReq) -> dict:
    return basis.income_tax(**req.model_dump())


@router.post("/tax/provisional", tags=["personal"])
def provisional(req: ProvisionalReq) -> dict:
    return basis.provisional_tax(**req.model_dump())


@router.post("/tax/cgt", tags=["personal"])
def cgt(req: CGTReq) -> dict:
    return basis.capital_gains_tax(**req.model_dump())


@router.post("/tax/retirement-lumpsum", tags=["retirement"])
def lumpsum(req: LumpSumReq) -> dict:
    return basis.lump_sum_tax(**req.model_dump())


@router.post("/tax/retirement-deduction", tags=["retirement"])
def ret_deduction(req: RetDeductionReq) -> dict:
    return basis.retirement_deduction(**req.model_dump())


@router.post("/tax/company", tags=["business"])
def company(req: AmountReq) -> dict:
    return basis.company_tax(taxable_income=req.amount)


@router.post("/tax/trust", tags=["business"])
def trust(req: AmountReq) -> dict:
    return basis.trust_tax(taxable_income=req.amount)


@router.post("/tax/dividends", tags=["business"])
def dividends(req: AmountReq) -> dict:
    return basis.dividends_tax(dividend=req.amount)


@router.post("/tax/donations", tags=["personal"])
def donations(req: DonationReq) -> dict:
    return basis.donations_tax(**req.model_dump())


@router.post("/tax/vat", tags=["indirect"])
def vat_endpoint(req: VatReq) -> dict:
    return basis.vat(**req.model_dump())


@router.post("/tax/turnover", tags=["business"])
def turnover(req: TurnoverReq) -> dict:
    return basis.turnover_tax(**req.model_dump())


@router.post("/tax/transfer-duty", tags=["indirect"])
def transfer(req: PropertyReq) -> dict:
    return basis.transfer_duty(**req.model_dump())


@router.post("/tax/uif", tags=["business"])
def uif_endpoint(req: UifReq) -> dict:
    return basis.uif(**req.model_dump())


@router.get("/tax/config", tags=["admin"])
def config() -> dict:
    """The full 2026/2027 rate book the hub calculates from."""
    c = CONFIG
    return {
        "year": c["year"], "period": c["period"],
        "individual_brackets": basis.bracket_rows(c["individual_brackets"]),
        "rebates": c["rebates"], "tax_thresholds": c["tax_thresholds"],
        "medical_credits": c["medical_credits"],
        "company_tax_rate": c["company_tax_rate"], "trust_tax_rate": c["trust_tax_rate"],
        "dividends_tax_rate": c["dividends_tax_rate"], "vat_rate": c["vat_rate"],
        "cgt": c["cgt"], "donations_tax": c["donations_tax"],
        "retirement_contribution": c["retirement_contribution"],
        "retirement_lump_sum_brackets": basis.bracket_rows(c["retirement_lump_sum_brackets"]),
        "withdrawal_brackets": basis.bracket_rows(c["withdrawal_brackets"]),
        "transfer_duty_brackets": basis.bracket_rows(c["transfer_duty_brackets"]),
        "turnover_tax_brackets": basis.bracket_rows(c["turnover_tax_brackets"]),
        "interest_exemption": c["interest_exemption"], "tfsa": c["tfsa"], "uif": c["uif"],
    }


app.include_router(router)
