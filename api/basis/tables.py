"""South African tax tables for the 2026/2027 tax year (1 Mar 2026 - 28 Feb 2027).

Source: SARS / 2026 Budget. The personal income tax brackets, rebates and
medical credits were adjusted by about 3.4% for inflation in the 2026 Budget.
Values here are the published figures; this is an illustrative calculation hub,
not tax advice.

To roll to a new year: copy this dict, update the numbers, point CONFIG at it.
"""

from __future__ import annotations

TAX_2026_2027 = {
    "year": "2026/2027",
    "period": "1 March 2026 to 28 February 2027",

    # Progressive individual (and special trust) income tax.
    # Each bracket: (lower_inclusive, upper_exclusive_or_None, base_tax, marginal_rate)
    "individual_brackets": [
        (0, 245_100, 0, 0.18),
        (245_100, 383_100, 44_118, 0.26),
        (383_100, 530_200, 79_998, 0.31),
        (530_200, 695_800, 125_599, 0.36),
        (695_800, 887_000, 185_215, 0.39),
        (887_000, 1_878_600, 259_783, 0.41),
        (1_878_600, None, 666_339, 0.45),
    ],

    "rebates": {"primary": 17_820, "secondary_65": 9_765, "tertiary_75": 3_249},
    # Age at which the tax threshold applies
    "tax_thresholds": {"under_65": 99_000, "age_65_to_74": 153_250, "age_75_plus": 171_300},

    # Medical scheme fees tax credit (per month)
    "medical_credits": {"main_member": 376, "first_dependant": 376, "additional_dependant": 254},
    "additional_medical_credit_rate": {"under_65": 0.25, "over_65_or_disabled": 0.3333},
    "additional_medical_income_floor": 0.075,  # 7.5% of taxable income (under 65)

    "company_tax_rate": 0.27,
    "trust_tax_rate": 0.45,         # non-special trusts
    "dividends_tax_rate": 0.20,
    "vat_rate": 0.15,

    # Retirement fund lump sum benefits on RETIREMENT or death (once-off table)
    "retirement_lump_sum_brackets": [
        (0, 550_000, 0, 0.0),
        (550_000, 770_000, 0, 0.18),
        (770_000, 1_155_000, 39_600, 0.27),
        (1_155_000, None, 143_550, 0.36),
    ],
    # Retirement fund lump sum WITHDRAWAL benefits (pre-retirement, incl. two-pot)
    "withdrawal_brackets": [
        (0, 27_500, 0, 0.0),
        (27_500, 726_000, 0, 0.18),
        (726_000, 1_089_000, 125_730, 0.27),
        (1_089_000, None, 223_740, 0.36),
    ],

    "cgt": {
        "annual_exclusion": 40_000,
        "death_exclusion": 300_000,
        "primary_residence_exclusion": 2_000_000,
        "individual_inclusion_rate": 0.40,
        "company_inclusion_rate": 0.80,
        "trust_inclusion_rate": 0.80,
    },

    "donations_tax": {
        "annual_exemption": 100_000,         # individuals
        "standard_rate": 0.20,
        "excess_rate": 0.25,                 # on cumulative donations above R30m
        "excess_threshold": 30_000_000,
    },

    "retirement_contribution": {"max_percent": 0.275, "annual_cap": 350_000},
    "interest_exemption": {"under_65": 23_800, "age_65_plus": 34_500},
    "tfsa": {"annual_limit": 36_000, "lifetime_limit": 500_000},

    # UIF: 1% employee + 1% employer, on remuneration capped monthly
    "uif": {"rate": 0.01, "monthly_ceiling": 17_712.0},
    "sdl": {"rate": 0.01, "annual_payroll_threshold": 500_000},

    # Transfer duty on property (natural persons and others)
    "transfer_duty_brackets": [
        (0, 1_210_000, 0, 0.0),
        (1_210_000, 1_663_800, 0, 0.03),
        (1_663_800, 2_329_300, 13_614, 0.06),
        (2_329_300, 2_994_800, 53_544, 0.08),
        (2_994_800, 13_310_000, 106_784, 0.11),
        (13_310_000, None, 1_241_456, 0.13),
    ],

    # Turnover tax for micro businesses (threshold raised to R2.3m from 1 Apr 2026)
    "turnover_tax_brackets": [
        (0, 600_000, 0, 0.0),
        (600_000, 950_000, 0, 0.01),
        (950_000, 1_400_000, 3_500, 0.02),
        (1_400_000, 2_300_000, 12_500, 0.03),
    ],
    "turnover_tax_max_turnover": 2_300_000,
}

CONFIG = TAX_2026_2027
