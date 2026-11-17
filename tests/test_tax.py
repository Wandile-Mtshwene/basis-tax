"""Validate SA tax calculations (2026/2027) against hand-computed SARS values."""

import pytest

import basis


def test_income_tax_600k():
    r = basis.income_tax(annual_income=600_000, age=40)
    # 125,599 + 36% of (600,000 - 530,200) = 150,727; less primary rebate 17,820
    assert r["tax_before_rebates"] == pytest.approx(150_727, abs=1)
    assert r["annual_tax"] == pytest.approx(132_907, abs=1)
    assert r["monthly_paye"] == pytest.approx(132_907 / 12, abs=0.5)
    assert r["marginal_rate"] == 0.36
    assert len(r["steps"]) >= 5


def test_below_tax_threshold_pays_nothing():
    r = basis.income_tax(annual_income=90_000, age=40)
    assert r["annual_tax"] == 0.0
    assert r["below_threshold"] is True


def test_age_rebates_increase_threshold():
    young = basis.income_tax(annual_income=150_000, age=40)["annual_tax"]
    old = basis.income_tax(annual_income=150_000, age=70)["annual_tax"]
    assert old < young  # extra secondary rebate


def test_medical_credits_applied():
    no_med = basis.income_tax(annual_income=400_000, age=40, medical_members=0)["annual_tax"]
    med = basis.income_tax(annual_income=400_000, age=40, medical_members=2)["annual_tax"]
    assert no_med - med == pytest.approx((376 + 376) * 12, abs=1)


def test_retirement_contribution_deducts():
    base = basis.income_tax(annual_income=600_000, age=40)["annual_tax"]
    withra = basis.income_tax(annual_income=600_000, age=40, retirement_contribution=100_000)["annual_tax"]
    assert withra < base


def test_cgt_individual():
    r = basis.capital_gains_tax(proceeds=2_000_000, base_cost=1_000_000,
                                taxpayer="individual", marginal_rate=0.45)
    # (1,000,000 - 40,000) * 40% * 45%
    assert r["taxable_gain"] == pytest.approx(384_000, abs=1)
    assert r["cgt"] == pytest.approx(172_800, abs=1)


def test_cgt_loss_no_tax():
    r = basis.capital_gains_tax(proceeds=500_000, base_cost=800_000)
    assert r["cgt"] == 0.0


def test_retirement_lumpsum_and_withdrawal():
    ret = basis.lump_sum_tax(amount=900_000, kind="retirement")
    assert ret["tax"] == pytest.approx(74_700, abs=1)   # 39,600 + 27% of 130,000
    wd = basis.lump_sum_tax(amount=900_000, kind="withdrawal")
    assert wd["tax"] == pytest.approx(172_710, abs=1)   # 125,730 + 27% of 174,000
    assert wd["tax"] > ret["tax"]


def test_company_and_trust():
    assert basis.company_tax(taxable_income=1_000_000)["tax"] == pytest.approx(270_000)
    assert basis.trust_tax(taxable_income=1_000_000)["tax"] == pytest.approx(450_000)


def test_dividends():
    r = basis.dividends_tax(dividend=100_000)
    assert r["tax"] == pytest.approx(20_000)
    assert r["net_dividend"] == pytest.approx(80_000)


def test_donations_tax():
    r = basis.donations_tax(amount=250_000)
    assert r["tax"] == pytest.approx(30_000)   # (250,000 - 100,000) * 20%


def test_vat_add_and_extract():
    add = basis.vat(amount=1_000, direction="add")
    assert add["vat"] == pytest.approx(150) and add["incl"] == pytest.approx(1_150)
    ext = basis.vat(amount=1_150, direction="extract")
    assert ext["vat"] == pytest.approx(150) and ext["excl"] == pytest.approx(1_000)


def test_turnover_tax():
    r = basis.turnover_tax(turnover=900_000)
    assert r["tax"] == pytest.approx(3_000)   # 1% of (900,000 - 600,000)
    assert basis.turnover_tax(turnover=3_000_000)["eligible"] is False


def test_transfer_duty():
    r = basis.transfer_duty(property_value=2_000_000)
    assert r["duty"] == pytest.approx(33_786, abs=1)   # 13,614 + 6% of 336,200
    assert basis.transfer_duty(property_value=1_000_000)["duty"] == 0.0


def test_uif_capped():
    r = basis.uif(monthly_remuneration=25_000)
    assert r["employee"] == pytest.approx(177.12, abs=0.01)
    assert r["total"] == pytest.approx(354.24, abs=0.01)


def test_provisional_split():
    r = basis.provisional_tax(estimated_taxable_income=600_000, age=40)
    assert r["first_payment"] == pytest.approx(r["estimated_annual_tax"] / 2, abs=1)


def test_every_result_has_steps():
    for res in [
        basis.income_tax(annual_income=500_000, age=40),
        basis.capital_gains_tax(proceeds=1_000_000, base_cost=500_000),
        basis.transfer_duty(property_value=3_000_000),
        basis.vat(amount=100),
    ]:
        assert res["steps"] and all("label" in s for s in res["steps"])
