import os

import pytest
from fastapi.testclient import TestClient

from app import app, route_priority

client = TestClient(app)

BASE = {"name": "Maya", "email": "maya@example.com"}


def dispute(**over):
    body = {**BASE, "dispute_type": "unauthorized", "merchant": "ShopX",
            "amount": 250, "currency": "USD", "statement_within_60_days": True}
    body.update(over)
    return client.post("/disputes", json=body)


def test_unauthorized_dispute_gets_provisional_credit_and_p2():
    r = dispute()
    assert r.status_code == 200
    b = r.json()
    assert b["case_id"].startswith("WF-D-")
    assert b["status"] == "opened"
    assert b["provisional_credit_eligible"] is True
    assert b["priority"] == "P2"
    assert b["expected_resolution_days"] == 30
    assert b["evidence_checklist"]
    assert b["confirmation_email"]["sent"] is False


def test_large_unauthorized_no_provisional_credit():
    assert dispute(amount=1500).json()["provisional_credit_eligible"] is False


def test_old_dispute_needs_manual_review():
    r = dispute(dispute_type="duplicate", statement_within_60_days=False, currency="EUR")
    assert r.json()["status"] == "needs_manual_review"
    assert r.json()["priority"] == "P3"


def test_bad_dispute_type_rejected():
    assert dispute(dispute_type="regret").status_code == 422


def test_full_card_number_rejected():
    assert dispute(merchant="4111 1111 1111 1111").status_code == 422


def test_idempotency_key_prevents_duplicates():
    h = {"Idempotency-Key": "abc-123"}
    body = {**BASE, "dispute_type": "duplicate", "merchant": "Cafe", "amount": 20, "currency": "EUR"}
    a = client.post("/disputes", json=body, headers=h).json()
    b = client.post("/disputes", json=body, headers=h).json()
    assert a["case_id"] == b["case_id"]


def test_flight_claim_and_lookup_with_timeline():
    r = client.post("/flight-claims", json={
        **BASE, "issue": "cancellation", "airline": "Demo Air",
        "flight_number": "DA101", "flight_date": "2026-11-01", "expenses_amount": 420,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["case_id"].startswith("WF-F-")
    assert body["max_cover_usd"] == 1500
    assert body["claim_deadline_days"] == 30
    g = client.get(f"/cases/{body['case_id']}").json()
    assert g["type"] == "flight_claim"
    assert g["timeline"][0]["stage"] == "received"
    assert g["next_steps"]


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


@pytest.mark.parametrize("text,flag,expected", [
    ("my card was stolen", False, "P1"),
    ("general question", True, "P1"),
    ("this is unacceptable, I want a complaint filed", False, "P2"),
    ("question about fees", False, "P3"),
])
def test_priority_routing(text, flag, expected):
    assert route_priority(text, flag) == expected


def test_handoff_priority_and_sla():
    r = client.post("/handoff-tickets", json={
        **BASE, "issue_type": "dispute", "summary": "I am stranded and my card was stolen",
        "preferred_contact": "phone",
    }).json()
    assert r["ticket_id"].startswith("WF-H-")
    assert r["priority"] == "P1"
    assert "15 minutes" in r["target_response"]


def test_feedback_and_metrics():
    assert client.post("/feedback", json={"rating": 5, "resolved_without_human": True}).json()["ok"]
    assert client.post("/feedback", json={"rating": 6}).status_code == 422
    m = client.get("/metrics").json()
    assert m["cases_total"] >= 1
    assert m["csat_responses"] >= 1
    assert 0 <= m["self_service_rate_pct"] <= 100
    assert m["estimated_agent_minutes_saved"] > 0


def test_evidence_checklist_endpoint():
    r = client.get("/evidence-checklist/duplicate").json()
    assert len(r["documents"]) == 3
    assert client.get("/evidence-checklist/nonsense").status_code == 422


def test_dashboard_served():
    r = client.get("/dashboard")
    assert r.status_code == 200 and "Wayfin Compass" in r.text


def test_unknown_case_404():
    assert client.get("/cases/WF-D-000000").status_code == 404


def test_api_key_enforced_when_set(monkeypatch):
    monkeypatch.setenv("WAYFIN_API_KEY", "secret")
    assert client.get("/cases/WF-D-000000").status_code == 401
    ok = client.get("/cases/WF-D-000000", headers={"X-API-Key": "secret"})
    assert ok.status_code == 404  # authorized, then not found
    monkeypatch.delenv("WAYFIN_API_KEY")


def comp(**over):
    body = {"distance_km": 1000, "arrival_delay_minutes": 200, "covered_route": True}
    body.update(over)
    return client.post("/airline-compensation/estimate", json=body).json()


def test_compensation_bands():
    assert comp(distance_km=1200)["indicative_amount_eur"] == 250
    assert comp(distance_km=2500)["indicative_amount_eur"] == 400
    assert comp(distance_km=5000, arrival_delay_minutes=300)["indicative_amount_eur"] == 600
    assert comp(distance_km=5000, arrival_delay_minutes=200)["indicative_amount_eur"] == 300


def test_compensation_delay_threshold_and_route():
    assert comp(arrival_delay_minutes=120)["verdict"] == "not_eligible"
    assert comp(covered_route=False)["verdict"] == "check_other_rules"


def test_compensation_cancellation_notice():
    assert comp(cancelled=True, cancellation_notice_days=20)["verdict"] == "not_eligible"
    assert comp(cancelled=True, cancellation_notice_days=3)["verdict"] == "likely_eligible"


def test_compensation_extraordinary_reasons():
    assert comp(reason="weather")["verdict"] == "airline_may_be_exempt"
    assert comp(reason="technical_fault")["verdict"] == "likely_eligible"


# ---- space evidence (network is faked, so tests never depend on NASA or NOAA) ----
import app as app_module  # noqa: E402


def _fake(events=None, kp=None, fail=False):
    def fetch(url, params=None):
        if fail:
            raise RuntimeError("down")
        if "eonet" in url:
            return {"events": events or []}
        return kp or []
    return fetch


STORM = {"title": "Tropical Storm Test", "categories": [{"id": "severeStorms"}],
         "geometry": [{"type": "Point", "date": "2026-11-05T00:00:00Z", "coordinates": [-73.9, 40.7]}]}


def space(**over):
    body = {"departure_airport": "lhr", "arrival_airport": "JFK", "flight_date": "2026-11-05"}
    body.update(over)
    return client.post("/space-evidence", json=body)


def test_space_storm_near_arrival_is_reported(monkeypatch):
    monkeypatch.setattr(app_module, "FETCH_JSON", _fake(events=[STORM]))
    b = space().json()
    assert b["status"] == "signals_found"
    assert b["signals"][0]["kind"] == "severeStorms"
    assert b["signals"][0]["where"] == "JFK"
    assert "not proof" in b["disclaimer"]


def test_space_kp_storm_reported(monkeypatch):
    kp = [{"time_tag": "2026-11-05T03:00:00", "Kp": 6.33}, {"time_tag": "2026-11-05T06:00:00", "Kp": 2.0}]
    monkeypatch.setattr(app_module, "FETCH_JSON", _fake(kp=kp))
    b = space(arrival_airport="LHR").json()
    assert any(s["kind"] == "geomagnetic_storm" for s in b["signals"])


def test_space_quiet_day_has_no_signals(monkeypatch):
    monkeypatch.setattr(app_module, "FETCH_JSON", _fake())
    assert space().json()["status"] == "no_signals"


def test_space_source_down_degrades_gracefully(monkeypatch):
    monkeypatch.setattr(app_module, "FETCH_JSON", _fake(fail=True))
    r = space()
    assert r.status_code == 200
    assert r.json()["status"] == "unavailable"


def test_space_unknown_airport_and_bad_date(monkeypatch):
    monkeypatch.setattr(app_module, "FETCH_JSON", _fake())
    assert space(departure_airport="ZZZ").status_code == 422
    assert space(flight_date="2026-13-45").status_code == 422
