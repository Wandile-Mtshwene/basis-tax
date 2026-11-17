"use client";

import { useEffect, useMemo, useState } from "react";
import { postTax, getConfig, zar, pct, type TaxResult } from "./lib/api";

type FieldKind = "number" | "pct" | "select" | "bool";
type Field = {
  name: string; label: string; kind: FieldKind; def: number | string | boolean;
  step?: number; options?: { value: string; label: string }[];
};
type Summary = { label: string; value: string; big?: boolean };
type Calc = {
  id: string; label: string; group: string; path: string; blurb: string;
  fields: Field[]; summary: (r: TaxResult) => Summary[];
};

const n = (r: TaxResult, k: string) => Number(r[k] ?? 0);

const CALCS: Calc[] = [
  {
    id: "income", label: "Income tax / PAYE", group: "Personal", path: "/api/tax/income",
    blurb: "Tax on taxable income with rebates and medical credits, and the monthly PAYE.",
    fields: [
      { name: "annual_income", label: "Annual income (R)", kind: "number", def: 600_000, step: 10_000 },
      { name: "age", label: "Age", kind: "number", def: 40, step: 1 },
      { name: "medical_members", label: "Medical scheme members", kind: "number", def: 0, step: 1 },
      { name: "retirement_contribution", label: "Retirement contribution (R)", kind: "number", def: 0, step: 5_000 },
    ],
    summary: (r) => [
      { label: "Monthly PAYE", value: zar(n(r, "monthly_paye")), big: true },
      { label: "Annual tax", value: zar(n(r, "annual_tax")) },
      { label: "Effective rate", value: pct(n(r, "effective_rate")) },
      { label: "Marginal rate", value: pct(n(r, "marginal_rate")) },
    ],
  },
  {
    id: "cgt", label: "Capital gains tax", group: "Personal", path: "/api/tax/cgt",
    blurb: "Gain less exclusions, included at the applicable rate, then taxed.",
    fields: [
      { name: "proceeds", label: "Proceeds (R)", kind: "number", def: 2_000_000, step: 100_000 },
      { name: "base_cost", label: "Base cost (R)", kind: "number", def: 1_000_000, step: 100_000 },
      { name: "taxpayer", label: "Taxpayer", kind: "select", def: "individual",
        options: [{ value: "individual", label: "Individual" }, { value: "company", label: "Company" }, { value: "trust", label: "Trust" }] },
      { name: "marginal_rate", label: "Marginal rate", kind: "pct", def: 0.45, step: 1 },
      { name: "is_primary_residence", label: "Primary residence", kind: "bool", def: false },
    ],
    summary: (r) => [
      { label: "Capital gains tax", value: zar(n(r, "cgt")), big: true },
      { label: "Taxable gain", value: zar(n(r, "taxable_gain")) },
      { label: "Effective rate", value: pct(n(r, "effective_rate")) },
    ],
  },
  {
    id: "donations", label: "Donations tax", group: "Personal", path: "/api/tax/donations",
    blurb: "Donations above the annual exemption are taxed at 20% (25% past R30m cumulative).",
    fields: [
      { name: "amount", label: "Donation (R)", kind: "number", def: 250_000, step: 25_000 },
      { name: "cumulative_prior", label: "Prior donations this year (R)", kind: "number", def: 0, step: 25_000 },
    ],
    summary: (r) => [
      { label: "Donations tax", value: zar(n(r, "tax")), big: true },
      { label: "Taxable donation", value: zar(n(r, "taxable_donation")) },
    ],
  },
  {
    id: "provisional", label: "Provisional tax", group: "Personal", path: "/api/tax/provisional",
    blurb: "Estimated annual tax split into two provisional payments.",
    fields: [
      { name: "estimated_taxable_income", label: "Estimated income (R)", kind: "number", def: 600_000, step: 10_000 },
      { name: "age", label: "Age", kind: "number", def: 40, step: 1 },
      { name: "already_paid", label: "Already paid (R)", kind: "number", def: 0, step: 5_000 },
    ],
    summary: (r) => [
      { label: "First payment", value: zar(n(r, "first_payment")), big: true },
      { label: "Second payment", value: zar(n(r, "second_payment")) },
      { label: "Estimated annual tax", value: zar(n(r, "estimated_annual_tax")) },
    ],
  },
  {
    id: "retirement-lumpsum", label: "Retirement lump sum", group: "Retirement", path: "/api/tax/retirement-lumpsum",
    blurb: "Tax on a retirement/death benefit or a pre-retirement withdrawal (two-pot).",
    fields: [
      { name: "amount", label: "Lump sum (R)", kind: "number", def: 900_000, step: 50_000 },
      { name: "kind", label: "Type", kind: "select", def: "retirement",
        options: [{ value: "retirement", label: "Retirement / death" }, { value: "withdrawal", label: "Withdrawal (two-pot)" }] },
    ],
    summary: (r) => [
      { label: "Tax", value: zar(n(r, "tax")), big: true },
      { label: "Net received", value: zar(n(r, "net")) },
      { label: "Effective rate", value: pct(n(r, "effective_rate")) },
    ],
  },
  {
    id: "retirement-deduction", label: "Retirement deduction", group: "Retirement", path: "/api/tax/retirement-deduction",
    blurb: "Deductible portion of a contribution (27.5% of income, capped at R350,000).",
    fields: [
      { name: "income", label: "Income (R)", kind: "number", def: 600_000, step: 10_000 },
      { name: "contribution", label: "Contribution (R)", kind: "number", def: 150_000, step: 10_000 },
    ],
    summary: (r) => [
      { label: "Deductible", value: zar(n(r, "deductible")), big: true },
      { label: "Carried forward", value: zar(n(r, "carried_forward")) },
    ],
  },
  {
    id: "company", label: "Company tax", group: "Business", path: "/api/tax/company",
    blurb: "Flat 27% on company taxable income.",
    fields: [{ name: "amount", label: "Taxable income (R)", kind: "number", def: 1_000_000, step: 100_000 }],
    summary: (r) => [
      { label: "Company tax", value: zar(n(r, "tax")), big: true },
      { label: "After tax", value: zar(n(r, "after_tax")) },
    ],
  },
  {
    id: "trust", label: "Trust tax", group: "Business", path: "/api/tax/trust",
    blurb: "Flat 45% on non-special trust taxable income.",
    fields: [{ name: "amount", label: "Taxable income (R)", kind: "number", def: 1_000_000, step: 100_000 }],
    summary: (r) => [
      { label: "Trust tax", value: zar(n(r, "tax")), big: true },
      { label: "After tax", value: zar(n(r, "after_tax")) },
    ],
  },
  {
    id: "dividends", label: "Dividends tax", group: "Business", path: "/api/tax/dividends",
    blurb: "20% dividends withholding tax.",
    fields: [{ name: "amount", label: "Dividend (R)", kind: "number", def: 100_000, step: 10_000 }],
    summary: (r) => [
      { label: "Dividends tax", value: zar(n(r, "tax")), big: true },
      { label: "Net dividend", value: zar(n(r, "net_dividend")) },
    ],
  },
  {
    id: "turnover", label: "Turnover tax", group: "Business", path: "/api/tax/turnover",
    blurb: "Micro-business turnover tax (eligible up to R2.3m turnover).",
    fields: [{ name: "turnover", label: "Annual turnover (R)", kind: "number", def: 900_000, step: 50_000 }],
    summary: (r) => [
      { label: "Turnover tax", value: zar(n(r, "tax")), big: true },
      { label: "Effective rate", value: pct(n(r, "effective_rate")) },
      { label: "Eligible", value: r["eligible"] ? "yes" : "no" },
    ],
  },
  {
    id: "uif", label: "UIF", group: "Business", path: "/api/tax/uif",
    blurb: "1% employee + 1% employer, on remuneration capped at R17,712/month.",
    fields: [{ name: "monthly_remuneration", label: "Monthly remuneration (R)", kind: "number", def: 25_000, step: 1_000 }],
    summary: (r) => [
      { label: "Employee", value: zar(n(r, "employee")), big: true },
      { label: "Employer", value: zar(n(r, "employer")) },
      { label: "Total", value: zar(n(r, "total")) },
    ],
  },
  {
    id: "vat", label: "VAT", group: "Indirect", path: "/api/tax/vat",
    blurb: "Add 15% VAT to a price, or extract the VAT from a VAT-inclusive price.",
    fields: [
      { name: "amount", label: "Amount (R)", kind: "number", def: 1_000, step: 100 },
      { name: "direction", label: "Direction", kind: "select", def: "add",
        options: [{ value: "add", label: "Add VAT" }, { value: "extract", label: "Extract VAT" }] },
    ],
    summary: (r) => [
      { label: "VAT", value: zar(n(r, "vat")), big: true },
      { label: "Excluding", value: zar(n(r, "excl")) },
      { label: "Including", value: zar(n(r, "incl")) },
    ],
  },
  {
    id: "transfer-duty", label: "Transfer duty", group: "Indirect", path: "/api/tax/transfer-duty",
    blurb: "Property transfer duty on a sliding scale (nil up to R1,210,000).",
    fields: [{ name: "property_value", label: "Property value (R)", kind: "number", def: 2_000_000, step: 100_000 }],
    summary: (r) => [
      { label: "Transfer duty", value: zar(n(r, "duty")), big: true },
      { label: "Effective rate", value: pct(n(r, "effective_rate")) },
    ],
  },
];

const GROUPS = ["Personal", "Retirement", "Business", "Indirect"];

function defaults(c: Calc): Record<string, number | string | boolean> {
  return Object.fromEntries(c.fields.map((f) => [f.name, f.def]));
}

export default function Home() {
  const [activeId, setActiveId] = useState("income");
  const [showRates, setShowRates] = useState(false);
  const calc = useMemo(() => CALCS.find((c) => c.id === activeId)!, [activeId]);
  const [values, setValues] = useState(() => defaults(calc));
  const [result, setResult] = useState<TaxResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function select(id: string) {
    setShowRates(false);
    setActiveId(id);
    setValues(defaults(CALCS.find((c) => c.id === id)!));
    setResult(null);
  }

  useEffect(() => {
    if (showRates) return;
    const t = setTimeout(async () => {
      setLoading(true); setError(null);
      try { setResult(await postTax(calc.path, values)); }
      catch (e) { setError(e instanceof Error ? e.message : "failed"); setResult(null); }
      finally { setLoading(false); }
    }, 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeId, JSON.stringify(values), showRates]);

  return (
    <div className="mx-auto max-w-6xl px-5 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">South African Tax Hub</h1>
        <p className="text-muted mt-1 max-w-3xl text-sm">
          Every major South African tax for the 2026/2027 year, calculated live and shown with the
          full working. Pick a tax on the left, change the inputs, and the answer and its explanation
          update as you type.
        </p>
      </div>

      <div className="grid lg:grid-cols-[230px_1fr] gap-5">
        {/* nav */}
        <nav className="card p-3 h-fit text-sm">
          {GROUPS.map((g) => (
            <div key={g} className="mb-2">
              <p className="field-label px-2 py-1">{g}</p>
              {CALCS.filter((c) => c.group === g).map((c) => (
                <button key={c.id} onClick={() => select(c.id)}
                  className={`w-full text-left px-2 py-1.5 rounded-md ${
                    !showRates && activeId === c.id ? "bg-accent text-[var(--accent-ink)] font-semibold" : "text-muted hover:text-foreground"}`}>
                  {c.label}
                </button>
              ))}
            </div>
          ))}
          <div className="border-t border-border pt-2 mt-1">
            <button onClick={() => setShowRates(true)}
              className={`w-full text-left px-2 py-1.5 rounded-md ${showRates ? "bg-accent text-[var(--accent-ink)] font-semibold" : "text-muted hover:text-foreground"}`}>
              Rate book 2026/27
            </button>
          </div>
        </nav>

        {showRates ? <RateBook /> : (
          <div className="grid md:grid-cols-[300px_1fr] gap-5">
            {/* form */}
            <div className="card p-5 h-fit">
              <h2 className="font-semibold">{calc.label}</h2>
              <p className="text-muted text-xs mt-1 mb-4">{calc.blurb}</p>
              <div className="space-y-3">
                {calc.fields.map((f) => (
                  <label key={f.name} className="block space-y-1">
                    <span className="field-label">{f.label}</span>
                    {f.kind === "select" ? (
                      <select value={String(values[f.name])}
                        onChange={(e) => setValues({ ...values, [f.name]: e.target.value })}>
                        {f.options!.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                      </select>
                    ) : f.kind === "bool" ? (
                      <select value={values[f.name] ? "yes" : "no"}
                        onChange={(e) => setValues({ ...values, [f.name]: e.target.value === "yes" })}>
                        <option value="no">no</option><option value="yes">yes</option>
                      </select>
                    ) : f.kind === "pct" ? (
                      <input type="number" step={f.step ?? 1} value={+(Number(values[f.name]) * 100).toFixed(2)}
                        onChange={(e) => setValues({ ...values, [f.name]: +e.target.value / 100 })} />
                    ) : (
                      <input type="number" step={f.step ?? 1} value={Number(values[f.name])}
                        onChange={(e) => setValues({ ...values, [f.name]: +e.target.value })} />
                    )}
                  </label>
                ))}
              </div>
              <p className="mt-4 text-xs text-muted flex items-center gap-2">
                <span className={`inline-block h-2 w-2 rounded-full ${loading ? "bg-warn" : "bg-positive"}`} />
                {loading ? "Calculating…" : "Updates live as you type"}
              </p>
              {error && <p className="text-warn text-xs mt-2">{error}</p>}
            </div>

            {/* result + explanation */}
            <div className="space-y-5">
              {result && (
                <>
                  <div className="card p-5 flex flex-wrap items-end gap-x-10 gap-y-3">
                    {calc.summary(result).map((s, i) => (
                      <div key={i}>
                        <div className="field-label">{s.label}</div>
                        <div className={s.big ? "text-4xl font-semibold text-accent" : "text-sm font-mono"}>{s.value}</div>
                      </div>
                    ))}
                  </div>
                  <div className="card p-5">
                    <h3 className="font-semibold mb-3">How this is worked out</h3>
                    <table className="w-full text-sm">
                      <tbody>
                        {result.steps.map((s, i) => (
                          <tr key={i} className="border-b border-border/50">
                            <td className="py-1.5 pr-3">{s.label}{s.note && <span className="text-muted text-xs block">{s.note}</span>}</td>
                            <td className="py-1.5 text-right font-mono whitespace-nowrap"
                              style={{ color: s.amount !== null && s.amount < 0 ? "#f87171" : undefined }}>
                              {s.amount === null ? "" : zar(s.amount)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <p className="text-muted text-xs mt-3">Tax year {String(result.tax_year ?? "2026/2027")}. Illustrative calculation, not tax advice.</p>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function RateBook() {
  const [cfg, setCfg] = useState<Record<string, unknown> | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => { getConfig().then(setCfg).catch((e) => setErr(String(e))); }, []);
  if (err) return <div className="card p-6 text-warn">{err}</div>;
  if (!cfg) return <div className="card p-6 text-muted">Loading rate book…</div>;

  const brackets = (rows: { from: number; to: number | null; base_tax: number; rate: number }[]) => (
    <table className="w-full text-sm">
      <thead className="text-muted text-left"><tr><th className="py-1">From</th><th>To</th><th>Base</th><th>Rate</th></tr></thead>
      <tbody className="font-mono">
        {rows.map((b, i) => (
          <tr key={i} className="border-t border-border/50">
            <td className="py-1">R{b.from.toLocaleString()}</td>
            <td>{b.to === null ? "and above" : "R" + b.to.toLocaleString()}</td>
            <td>R{b.base_tax.toLocaleString()}</td>
            <td>{(b.rate * 100).toFixed(0)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
  const g = (k: string) => cfg[k] as never;

  return (
    <div className="space-y-5">
      <div className="card p-5">
        <h2 className="font-semibold mb-1">Rate book {String(cfg.year)}</h2>
        <p className="text-muted text-sm">{String(cfg.period)}. Every figure the hub calculates from, served live from the API.</p>
      </div>
      <div className="grid md:grid-cols-2 gap-5">
        <div className="card p-5"><h3 className="font-semibold mb-3">Individual income tax</h3>{brackets(g("individual_brackets"))}</div>
        <div className="card p-5">
          <h3 className="font-semibold mb-3">Rebates, thresholds, credits</h3>
          <Kv o={cfg.rebates as Record<string, number>} money />
          <div className="mt-2" /><Kv o={cfg.tax_thresholds as Record<string, number>} money />
          <div className="mt-2" /><Kv o={cfg.medical_credits as Record<string, number>} money suffix="/mo" />
        </div>
        <div className="card p-5"><h3 className="font-semibold mb-3">Retirement lump sum (retirement/death)</h3>{brackets(g("retirement_lump_sum_brackets"))}</div>
        <div className="card p-5"><h3 className="font-semibold mb-3">Retirement withdrawal</h3>{brackets(g("withdrawal_brackets"))}</div>
        <div className="card p-5"><h3 className="font-semibold mb-3">Transfer duty</h3>{brackets(g("transfer_duty_brackets"))}</div>
        <div className="card p-5"><h3 className="font-semibold mb-3">Turnover tax</h3>{brackets(g("turnover_tax_brackets"))}</div>
        <div className="card p-5 md:col-span-2">
          <h3 className="font-semibold mb-3">Flat rates and limits</h3>
          <div className="grid sm:grid-cols-2 gap-x-10 gap-y-1">
            <Row k="Company tax" v={pct(Number(cfg.company_tax_rate))} />
            <Row k="Trust tax" v={pct(Number(cfg.trust_tax_rate))} />
            <Row k="Dividends tax" v={pct(Number(cfg.dividends_tax_rate))} />
            <Row k="VAT" v={pct(Number(cfg.vat_rate))} />
            <Row k="CGT individual inclusion" v={pct((cfg.cgt as Record<string, number>).individual_inclusion_rate)} />
            <Row k="CGT annual exclusion" v={zar((cfg.cgt as Record<string, number>).annual_exclusion)} />
            <Row k="Retirement deduction cap" v={zar((cfg.retirement_contribution as Record<string, number>).annual_cap)} />
            <Row k="TFSA annual / lifetime" v={`${zar((cfg.tfsa as Record<string, number>).annual_limit)} / ${zar((cfg.tfsa as Record<string, number>).lifetime_limit)}`} />
          </div>
        </div>
      </div>
    </div>
  );
}

function Kv({ o, money, suffix = "" }: { o: Record<string, number>; money?: boolean; suffix?: string }) {
  return <>{Object.entries(o).map(([k, v]) => (
    <Row key={k} k={k.replace(/_/g, " ")} v={(money ? zar(v) : String(v)) + suffix} />
  ))}</>;
}
function Row({ k, v }: { k: string; v: string }) {
  return <div className="flex justify-between text-sm gap-4 py-0.5"><span className="text-muted">{k}</span><span className="font-mono">{v}</span></div>;
}
