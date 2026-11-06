from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

BASE = {"name": "Maya", "email": "maya@example.com"}


def test_unauthorized_dispute_gets_provisional_credit():
    r = client.post("/disputes", json={
        **BASE, "dispute_type": "unauthorized", "merchant": "ShopX",
        "amount": 250, "currency": "USD", "statement_within_60_days": True,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["case_id"].startswith("WF-D-")
    assert body["status"] == "opened"
    assert body["provisional_credit_eligible"] is True
    assert body["expected_resolution_days"] == 30


def test_large_unauthorized_no_provisional_credit():
    r = client.post("/disputes", json={
        **BASE, "dispute_type": "unauthorized", "merchant": "ShopX",
        "amount": 1500, "currency": "USD",
    })
    assert r.json()["provisional_credit_eligible"] is False


def test_old_dispute_needs_manual_review():
    r = client.post("/disputes", json={
        **BASE, "dispute_type": "duplicate", "merchant": "Cafe",
        "amount": 20, "currency": "EUR", "statement_within_60_days": False,
    })
    assert r.json()["status"] == "needs_manual_review"


def test_bad_dispute_type_rejected():
    r = client.post("/disputes", json={
        **BASE, "dispute_type": "regret", "merchant": "X", "amount": 5, "currency": "USD",
    })
    assert r.status_code == 422


def test_flight_claim_and_lookup():
    r = client.post("/flight-claims", json={
        **BASE, "issue": "cancellation", "airline": "Demo Air",
        "flight_number": "DA101", "flight_date": "2026-11-01", "expenses_amount": 420,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["case_id"].startswith("WF-F-")
    assert body["max_cover_usd"] == 1500
    assert body["claim_deadline_days"] == 30
    g = client.get(f"/cases/{body['case_id']}")
    assert g.status_code == 200
    assert g.json()["type"] == "flight_claim"


def test_short_delay_goes_to_review():
    r = client.post("/flight-claims", json={
        **BASE, "issue": "delay", "airline": "Demo Air", "flight_number": "DA7",
        "flight_date": "2026-11-01", "expenses_amount": 30, "delay_hours": 2,
    })
    assert r.json()["status"] == "needs_manual_review"


def test_bad_date_rejected():
    r = client.post("/flight-claims", json={
        **BASE, "issue": "delay", "airline": "A", "flight_number": "1",
        "flight_date": "01/11/2026", "expenses_amount": 0,
    })
    assert r.status_code == 422


def test_replacement_standard_and_express():
    s = client.post("/replacement-cards", json=BASE).json()
    assert s["fee_usd"] == 0 and s["delivery_business_days"] == "5 to 7"
    e = client.post("/replacement-cards", json={**BASE, "express": True}).json()
    assert e["fee_usd"] == 15 and e["delivery_business_days"] == "2 to 3"


def test_handoff_ticket():
    r = client.post("/handoff-tickets", json={
        **BASE, "issue_type": "dispute", "summary": "Customer wants a person.",
        "preferred_contact": "phone",
    })
    assert r.json()["ticket_id"].startswith("WF-H-")


def test_unknown_case_404():
    assert client.get("/cases/WF-D-000000").status_code == 404
