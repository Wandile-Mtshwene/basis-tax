import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SA Tax Hub — 2026/2027",
  description:
    "A hub for South African tax calculations (2026/2027): income tax and PAYE, CGT, retirement, company, dividends, VAT, transfer duty and more, each explained step by step.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <header className="border-b border-border bg-surface/60 backdrop-blur sticky top-0 z-10">
          <div className="mx-auto max-w-6xl px-5 h-14 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 font-semibold">
              <span className="inline-block h-5 w-5 rounded bg-accent" />
              SA Tax<span className="text-muted font-normal">Hub</span>
            </Link>
            <nav className="flex items-center gap-5 text-sm text-muted">
              <span className="hidden sm:inline">2026/2027 tax year</span>
              <a href="/api/docs" target="_blank" rel="noreferrer" className="hover:text-foreground">API docs ↗</a>
              <a href="https://github.com/Wandile-Mtshwene/basis-tax" target="_blank" rel="noreferrer" className="hover:text-foreground">GitHub ↗</a>
            </nav>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-border text-muted text-xs">
          <div className="mx-auto max-w-6xl px-5 py-4 flex flex-wrap gap-x-6 gap-y-1 justify-between">
            <span>South African tax calculations · Python · FastAPI · Next.js</span>
            <span>Figures per SARS 2026/2027. A calculation and explanation hub, not tax advice.</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
