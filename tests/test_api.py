"""Smoke tests for the SA Tax Hub API."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["tax_year"] == "2026/2027"


def test_income_endpoint():
    r = client.post("/api/tax/income", json={"annual_income": 600_000, "age": 40})
    assert r.status_code == 200
    assert r.json()["annual_tax"] > 0


def test_all_endpoints_respond():
    checks = [
        ("/api/tax/cgt", {"proceeds": 2_000_000, "base_cost": 1_000_000}),
        ("/api/tax/retirement-lumpsum", {"amount": 900_000, "kind": "retirement"}),
        ("/api/tax/company", {"amount": 1_000_000}),
        ("/api/tax/dividends", {"amount": 100_000}),
        ("/api/tax/vat", {"amount": 1_000, "direction": "add"}),
        ("/api/tax/turnover", {"turnover": 900_000}),
        ("/api/tax/transfer-duty", {"property_value": 2_000_000}),
        ("/api/tax/uif", {"monthly_remuneration": 25_000}),
    ]
    for path, body in checks:
        assert client.post(path, json=body).status_code == 200, path


def test_config_endpoint():
    c = client.get("/api/tax/config").json()
    assert c["year"] == "2026/2027"
    assert len(c["individual_brackets"]) == 7
