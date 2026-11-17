// SA Tax Hub API client. Local dev talks to the FastAPI dev server on :8000;
// deployed, requests go same-origin to the Python function at /api.
const RAW = process.env.NEXT_PUBLIC_API_URL;
function resolveBase(): string {
  if (RAW !== undefined) return RAW.replace(/\/$/, "");
  if (typeof window !== "undefined") {
    const h = window.location.hostname;
    if (h !== "localhost" && h !== "127.0.0.1") return "";
  }
  return "http://127.0.0.1:8000";
}
export const API_URL = resolveBase();

export type Step = { label: string; amount: number | null; note: string };
export type TaxResult = Record<string, unknown> & { steps: Step[]; tax_year?: string };

export async function postTax(path: string, body: Record<string, unknown>): Promise<TaxResult> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function getConfig(): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_URL}/api/tax/config`);
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

export const zar = (n: number) =>
  new Intl.NumberFormat("en-ZA", { style: "currency", currency: "ZAR", maximumFractionDigits: 2 }).format(n);
export const pct = (n: number) => `${(n * 100).toFixed(2)}%`;
