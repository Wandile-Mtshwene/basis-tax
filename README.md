# SA Tax Hub — 2026/2027

A hub for South African tax calculations for the 2026/2027 tax year, each shown
with its full step-by-step working. A Next.js front end over a Python (FastAPI)
tax engine, deployed as one Vercel project. Part of a portfolio of actuarial and
quantitative apps.

It is a **calculation and explanation hub, not payroll or tax advice.**

## Taxes covered

- **Personal income tax / PAYE** — brackets, rebates, medical credits, retirement deduction
- **Provisional tax** — the two provisional payments
- **Capital gains tax** — individual, company, trust; exclusions and inclusion rates
- **Retirement** — lump-sum (retirement/death), withdrawal (two-pot), deduction cap
- **Company** (27%) and **trust** (45%) income tax
- **Dividends** withholding tax (20%)
- **Donations tax**
- **VAT** (add or extract, 15%)
- **Turnover tax** for micro businesses (up to R2.3m turnover)
- **Transfer duty** on property
- **UIF** (employee + employer, capped)

Every result includes a `steps` trace so you can see exactly how the number was reached.
A live **Rate book** view shows the full 2026/2027 figures served from the API.

## Figures

Based on SARS 2026/2027: individual brackets 18% to R245,100 up to 45% above
R1,878,600; primary rebate R17,820; medical credits R376 / R254; VAT 15%;
company 27%; retirement deduction capped at 27.5% of income or R350,000.

## Run locally

```bash
uv sync
cd api && uv run uvicorn main:app --reload   # http://127.0.0.1:8000/api/docs
cd .. && npm install && npm run dev           # http://localhost:3000
uv run pytest -q
```

## Deploy

```bash
vercel --prod
```

The engine lives under `api/basis/`; the serverless entrypoint is `api/index.py`.
Figures are validated against hand-computed SARS values in `tests/`. MIT licensed.
