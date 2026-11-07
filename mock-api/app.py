"""Wayfin Compass: actions service (v2).

An in-memory API that lets the Compass AI agent take real actions: open a
dispute, file a flight claim, order a replacement card, create a priority-
routed handoff ticket, look up a case with its timeline, collect CSAT, and
report business metrics. Demo only: no real card data is stored or accepted.

Modern API practices included:
  * optional API-key auth (set WAYFIN_API_KEY to enforce it)
  * idempotency keys so a retried action never creates a duplicate case
  * strict input validation, and a guard that rejects full card numbers
  * priority routing for urgent or high-risk situations
  * confirmation-email previews (nothing is actually sent)
  * live metrics and a small business dashboard at /dashboard
"""
from __future__ import annotations

import itertools
import os
import re
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field, field_validator

app = FastAPI(
    title="Wayfin Compass Actions API",
    description="Actions for the Wayfin Compass support agent (demo).",
    version="2.0.0",
)

# --------------------------------------------------------------------------
# Plumbing
# --------------------------------------------------------------------------
_counters = {
    "D": itertools.count(104827),
    "F": itertools.count(208315),
    "R": itertools.count(310442),
    "H": itertools.count(412096),
}
CASES: Dict[str, dict] = {}
FEEDBACK: List[dict] = []
_IDEMPOTENT: Dict[str, dict] = {}

AGENT_MINUTES_SAVED = {"dispute": 12, "flight_claim": 15, "replacement_card": 6}  # illustrative


def require_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    """Enforce an API key only when WAYFIN_API_KEY is set (open in local demo)."""
    expected = os.environ.get("WAYFIN_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key")


def _new_id(kind: str) -> str:
    return f"WF-{kind}-{next(_counters[kind])}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _save(case_id: str, case_type: str, status: str, payload: dict, next_steps: List[str],
          priority: str = "P3") -> None:
    CASES[case_id] = {
        "case_id": case_id,
        "type": case_type,
        "status": status,
        "priority": priority,
        "created_at": _now(),
        "timeline": [{"stage": "received", "at": _now()}],
        "next_steps": next_steps,
        "details": payload,
    }


def _email_preview(email: str, subject: str) -> dict:
    return {"to": email, "subject": subject, "sent": False, "note": "Preview only in this demo"}


def _idempotent(scope: str, key: Optional[str]):
    """Return a cached response for a repeated request with the same key."""
    if key:
        return _IDEMPOTENT.get(f"{scope}:{key}")
    return None


def _remember(scope: str, key: Optional[str], response: BaseModel) -> None:
    if key:
        _IDEMPOTENT[f"{scope}:{key}"] = response.model_dump(mode="json")


# Guard: never accept something that looks like a full card number.
_CARD_LIKE = re.compile(r"(?:\d[ -]?){13,19}")


def _reject_card_numbers(value: Optional[str]) -> Optional[str]:
    if value and _CARD_LIKE.search(value):
        raise ValueError("Do not enter full card numbers. Use only the last 4 digits.")
    return value


# --------------------------------------------------------------------------
# Evidence checklists (mirror knowledge/02-card-disputes-policy.md)
# --------------------------------------------------------------------------
class DisputeType(str, Enum):
    unauthorized = "unauthorized"
    duplicate = "duplicate"
    not_received = "not_received"
    not_as_described = "not_as_described"
    wrong_amount = "wrong_amount"
    cancelled_subscription = "cancelled_subscription"


EVIDENCE: Dict[DisputeType, List[str]] = {
    DisputeType.unauthorized: [
        "Date and amount of each charge you do not recognize",
        "When you last had the card in your possession",
        "Police report only if you report theft and want it on file (not required)",
    ],
    DisputeType.duplicate: [
        "Dates and amounts of both charges",
        "Merchant name",
        "Receipt or order confirmation showing a single purchase",
    ],
    DisputeType.not_received: [
        "Order confirmation and promised delivery date",
        "Proof you contacted the merchant (email or chat screenshot)",
        "Tracking details if the item was shipped",
    ],
    DisputeType.not_as_described: [
        "Order confirmation and the listing or description",
        "Photos of the item",
        "Proof of attempted return or merchant contact",
    ],
    DisputeType.wrong_amount: [
        "Receipt showing the agreed amount",
        "The amount actually charged",
        "Note if you declined to be charged in your home currency",
    ],
    DisputeType.cancelled_subscription: [
        "Date you cancelled",
        "The merchant's cancellation confirmation",
    ],
}


@app.get("/evidence-checklist/{dispute_type}", dependencies=[Depends(require_key)])
def evidence_checklist(dispute_type: DisputeType) -> dict:
    return {"dispute_type": dispute_type, "documents": EVIDENCE[dispute_type]}


# --------------------------------------------------------------------------
# Disputes
# --------------------------------------------------------------------------
class DisputeIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    dispute_type: DisputeType
    merchant: str = Field(min_length=1, max_length=120)
    amount: float = Field(gt=0, lt=1_000_000)
    currency: str = Field(min_length=3, max_length=3, description="ISO code, e.g. USD")
    statement_within_60_days: bool = True
    card_last4: Optional[str] = Field(default=None, pattern=r"^\d{4}$")
    urgent: bool = False

    @field_validator("merchant", "name")
    @classmethod
    def _no_card_numbers(cls, v: str) -> str:
        return _reject_card_numbers(v)  # type: ignore[return-value]


class DisputeOut(BaseModel):
    case_id: str
    status: str
    priority: str
    expected_resolution_days: int
    provisional_credit_eligible: bool
    evidence_checklist: List[str]
    message: str
    confirmation_email: dict


@app.post("/disputes", response_model=DisputeOut, dependencies=[Depends(require_key)])
def open_dispute(body: DisputeIn, idempotency_key: Optional[str] = Header(default=None)) -> DisputeOut:
    cached = _idempotent("dispute", idempotency_key)
    if cached:
        return DisputeOut(**cached)

    case_id = _new_id("D")
    if not body.statement_within_60_days:
        status = "needs_manual_review"
        message = ("The 60-day window has passed, so a specialist will review this case. "
                   "Approval is not guaranteed.")
    else:
        status = "opened"
        message = "Case opened. A confirmation email is on its way."
    provisional = (
        body.dispute_type == DisputeType.unauthorized
        and body.currency.upper() == "USD"
        and body.amount <= 1000
        and body.statement_within_60_days
    )
    priority = "P2" if (body.dispute_type == DisputeType.unauthorized or body.urgent) else "P3"
    next_steps = [
        "Wayfin contacts the merchant and reviews your evidence",
        "You receive the outcome by email (most cases within 30 days, up to 90)",
        "If the dispute is declined you may appeal once within 30 days",
    ]
    if provisional:
        next_steps.insert(0, "Provisional credit is applied within 5 business days")
    _save(case_id, "dispute", status, body.model_dump(mode="json"), next_steps, priority)

    out = DisputeOut(
        case_id=case_id,
        status=status,
        priority=priority,
        expected_resolution_days=30,
        provisional_credit_eligible=provisional,
        evidence_checklist=EVIDENCE[body.dispute_type],
        message=message,
        confirmation_email=_email_preview(body.email, f"Your Wayfin dispute {case_id}"),
    )
    _remember("dispute", idempotency_key, out)
    return out


# --------------------------------------------------------------------------
# Flight claims
# --------------------------------------------------------------------------
class FlightIssue(str, Enum):
    delay = "delay"
    cancellation = "cancellation"
    baggage = "baggage"


class FlightClaimIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    issue: FlightIssue
    airline: str = Field(min_length=1, max_length=80)
    flight_number: str = Field(min_length=1, max_length=12)
    flight_date: str = Field(description="YYYY-MM-DD")
    expenses_amount: float = Field(ge=0, lt=1_000_000, description="USD")
    delay_hours: Optional[float] = Field(default=None, ge=0, le=240)
    urgent: bool = False


class FlightClaimOut(BaseModel):
    case_id: str
    status: str
    priority: str
    claim_deadline_days: int
    documents_needed: List[str]
    max_cover_usd: float
    message: str
    confirmation_email: dict


COVER = {
    FlightIssue.delay: (75.0, "Meals and refreshments, up to USD 75 per day"),
    FlightIssue.cancellation: (1500.0, "Prepaid non-refundable trip costs, up to USD 1,500"),
    FlightIssue.baggage: (200.0, "Essential items, up to USD 200"),
}


@app.post("/flight-claims", response_model=FlightClaimOut, dependencies=[Depends(require_key)])
def file_flight_claim(body: FlightClaimIn,
                      idempotency_key: Optional[str] = Header(default=None)) -> FlightClaimOut:
    cached = _idempotent("flight", idempotency_key)
    if cached:
        return FlightClaimOut(**cached)
    try:
        datetime.strptime(body.flight_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="flight_date must be YYYY-MM-DD")

    cap, cover_text = COVER[body.issue]
    status = "opened"
    message = f"Claim opened. Cover: {cover_text}."
    if body.issue == FlightIssue.delay and body.delay_hours is not None and body.delay_hours < 4:
        status = "needs_manual_review"
        message = "Delays under 4 hours are outside standard cover; a specialist will review."
    if body.issue == FlightIssue.baggage and body.delay_hours is not None and body.delay_hours < 6:
        status = "needs_manual_review"
        message = "Baggage delays under 6 hours are outside standard cover; a specialist will review."

    docs = [
        "Booking confirmation or ticket showing payment with the Wayfin card",
        "Airline notice or email showing the delay or cancellation",
        "Receipts for expenses",
    ]
    case_id = _new_id("F")
    priority = "P2" if body.urgent else "P3"
    next_steps = [
        "Email your documents to support@wayfin.example with your case number",
        "Claims must be filed within 30 days of the disruption",
        "Claim from the airline first where the airline is responsible",
    ]
    _save(case_id, "flight_claim", status, body.model_dump(mode="json"), next_steps, priority)
    out = FlightClaimOut(
        case_id=case_id, status=status, priority=priority, claim_deadline_days=30,
        documents_needed=docs, max_cover_usd=cap, message=message,
        confirmation_email=_email_preview(body.email, f"Your Wayfin travel claim {case_id}"),
    )
    _remember("flight", idempotency_key, out)
    return out


# --------------------------------------------------------------------------
# Replacement card
# --------------------------------------------------------------------------
class ReplacementIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    express: bool = False


class ReplacementOut(BaseModel):
    request_id: str
    delivery_business_days: str
    fee_usd: float
    confirmation_email: dict


@app.post("/replacement-cards", response_model=ReplacementOut, dependencies=[Depends(require_key)])
def order_replacement(body: ReplacementIn,
                      idempotency_key: Optional[str] = Header(default=None)) -> ReplacementOut:
    cached = _idempotent("replacement", idempotency_key)
    if cached:
        return ReplacementOut(**cached)
    request_id = _new_id("R")
    days, fee = ("2 to 3", 15.0) if body.express else ("5 to 7", 0.0)
    _save(request_id, "replacement_card", "ordered", body.model_dump(mode="json"),
          [f"Your card arrives in {days} business days", "Freeze the old card in the app until then"],
          "P2")
    out = ReplacementOut(request_id=request_id, delivery_business_days=days, fee_usd=fee,
                         confirmation_email=_email_preview(body.email, f"Replacement card {request_id}"))
    _remember("replacement", idempotency_key, out)
    return out


# --------------------------------------------------------------------------
# Handoff with priority routing
# --------------------------------------------------------------------------
URGENT_WORDS = ("stolen", "fraud", "scam", "hacked", "emergency", "stranded", "unsafe", "urgent")
DISTRESS_WORDS = ("complaint", "angry", "furious", "unacceptable", "lawyer", "desperate", "scared")


def route_priority(text: str, urgent_flag: bool) -> str:
    t = text.lower()
    if urgent_flag or any(w in t for w in URGENT_WORDS):
        return "P1"
    if any(w in t for w in DISTRESS_WORDS):
        return "P2"
    return "P3"


class HandoffIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    issue_type: str = Field(max_length=60)
    summary: str = Field(min_length=1, max_length=1500)
    preferred_contact: str = Field(description="phone, email, or callback")
    urgent: bool = False

    @field_validator("summary")
    @classmethod
    def _no_card_numbers(cls, v: str) -> str:
        return _reject_card_numbers(v)  # type: ignore[return-value]


class HandoffOut(BaseModel):
    ticket_id: str
    status: str
    priority: str
    target_response: str


SLA = {"P1": "Within 15 minutes (phone)", "P2": "Within 2 hours", "P3": "Within 1 business day"}


@app.post("/handoff-tickets", response_model=HandoffOut, dependencies=[Depends(require_key)])
def create_handoff(body: HandoffIn,
                   idempotency_key: Optional[str] = Header(default=None)) -> HandoffOut:
    cached = _idempotent("handoff", idempotency_key)
    if cached:
        return HandoffOut(**cached)
    ticket_id = _new_id("H")
    priority = route_priority(f"{body.issue_type} {body.summary}", body.urgent)
    _save(ticket_id, "handoff", "queued", body.model_dump(mode="json"),
          [f"A Wayfin specialist will contact you ({SLA[priority].lower()})"], priority)
    out = HandoffOut(ticket_id=ticket_id, status="queued", priority=priority,
                     target_response=SLA[priority])
    _remember("handoff", idempotency_key, out)
    return out


# --------------------------------------------------------------------------
# Case lookup with timeline
# --------------------------------------------------------------------------
class DelayReason(str, Enum):
    none_given = "none_given"
    weather = "weather"
    air_traffic_control = "air_traffic_control"
    external_strike = "external_strike"
    security_risk = "security_risk"
    technical_fault = "technical_fault"
    crew_issue = "crew_issue"
    other = "other"


# Reasons airlines commonly argue are "extraordinary circumstances".
_MAY_BE_EXEMPT = {
    DelayReason.weather, DelayReason.air_traffic_control,
    DelayReason.external_strike, DelayReason.security_risk,
}


class CompensationIn(BaseModel):
    distance_km: float = Field(gt=0, le=20000)
    arrival_delay_minutes: int = Field(ge=0, le=5000)
    cancelled: bool = False
    cancellation_notice_days: Optional[int] = Field(default=None, ge=0, le=365)
    covered_route: bool = Field(description="Customer says the flight left an EU/UK airport, or arrived in the EU/UK on an EU/UK airline")
    intra_eu: bool = False
    reason: DelayReason = DelayReason.none_given


class CompensationOut(BaseModel):
    verdict: str
    indicative_amount_eur: float
    reasons: List[str]
    disclaimer: str


DISCLAIMER = ("Indicative general information about EU/UK261-style rules, not legal advice. "
              "The airline or a national enforcement body decides each case.")


@app.post("/airline-compensation/estimate", response_model=CompensationOut,
          dependencies=[Depends(require_key)])
def estimate_airline_compensation(body: CompensationIn) -> CompensationOut:
    """Deterministic estimate, so the amount never comes from a language model's guess."""
    why: List[str] = []
    if not body.covered_route:
        return CompensationOut(
            verdict="check_other_rules", indicative_amount_eur=0.0,
            reasons=["EU/UK rules may not apply to this route. Check the aviation authority of the countries involved."],
            disclaimer=DISCLAIMER)

    if body.cancelled:
        notice = body.cancellation_notice_days
        if notice is not None and notice >= 14:
            return CompensationOut(
                verdict="not_eligible", indicative_amount_eur=0.0,
                reasons=["Cancellations announced 14 or more days ahead usually do not qualify for fixed compensation. Refund or re-routing still applies."],
                disclaimer=DISCLAIMER)
        why.append("Cancelled with less than 14 days notice (or notice unknown).")
    else:
        if body.arrival_delay_minutes < 180:
            return CompensationOut(
                verdict="not_eligible", indicative_amount_eur=0.0,
                reasons=["Fixed compensation usually needs an arrival delay of 3 hours or more."],
                disclaimer=DISCLAIMER)
        why.append("Arrival delay is 3 hours or more.")

    if body.distance_km <= 1500:
        amount = 250.0
    elif body.distance_km <= 3500 or body.intra_eu:
        amount = 400.0
    else:
        amount = 600.0
        if not body.cancelled and body.arrival_delay_minutes < 240:
            amount = 300.0
            why.append("Long-haul delay under 4 hours is commonly reduced by half.")
    why.append(f"Distance band for {body.distance_km:.0f} km gives EUR {amount:.0f}.")

    if body.reason in _MAY_BE_EXEMPT:
        why.append("The airline may argue extraordinary circumstances; it must prove them.")
        verdict = "airline_may_be_exempt"
    else:
        if body.reason in (DelayReason.technical_fault, DelayReason.crew_issue):
            why.append("Ordinary technical or crew problems are generally not treated as extraordinary.")
        verdict = "likely_eligible"
    return CompensationOut(verdict=verdict, indicative_amount_eur=amount, reasons=why,
                           disclaimer=DISCLAIMER)


@app.get("/cases/{case_id}", dependencies=[Depends(require_key)])
def get_case(case_id: str) -> dict:
    case = CASES.get(case_id.upper())
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    keys = ("case_id", "type", "status", "priority", "created_at", "timeline", "next_steps")
    return {k: case[k] for k in keys}


# --------------------------------------------------------------------------
# Feedback (CSAT)
# --------------------------------------------------------------------------
class FeedbackIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    case_id: Optional[str] = None
    resolved_without_human: Optional[bool] = None
    comment: Optional[str] = Field(default=None, max_length=500)

    @field_validator("comment")
    @classmethod
    def _no_card_numbers(cls, v: Optional[str]) -> Optional[str]:
        return _reject_card_numbers(v)


@app.post("/feedback", dependencies=[Depends(require_key)])
def submit_feedback(body: FeedbackIn) -> dict:
    FEEDBACK.append({**body.model_dump(), "at": _now()})
    return {"ok": True, "message": "Thank you for your feedback."}


# --------------------------------------------------------------------------
# Metrics and dashboard
# --------------------------------------------------------------------------
@app.get("/metrics")
def metrics() -> dict:
    by_type: Dict[str, int] = {}
    for c in CASES.values():
        by_type[c["type"]] = by_type.get(c["type"], 0) + 1
    handoffs = by_type.get("handoff", 0)
    self_served = sum(n for t, n in by_type.items() if t != "handoff")
    minutes = sum(AGENT_MINUTES_SAVED.get(t, 0) * n for t, n in by_type.items())
    ratings = [f["rating"] for f in FEEDBACK]
    total = self_served + handoffs
    return {
        "cases_total": total,
        "cases_by_type": by_type,
        "self_served_cases": self_served,
        "handoffs": handoffs,
        "self_service_rate_pct": round(100 * self_served / total, 1) if total else 0.0,
        "csat_average": round(sum(ratings) / len(ratings), 2) if ratings else None,
        "csat_responses": len(ratings),
        "estimated_agent_minutes_saved": minutes,
        "assumptions_note": "Minutes saved use illustrative per-case assumptions: dispute 12, claim 15, replacement 6.",
    }


DASHBOARD_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wayfin Compass: Support Impact</title>
<style>
:root{--bg:#0b1020;--card:#141b34;--ink:#eef2ff;--muted:#9aa6cf;--accent:#5eead4;--accent2:#818cf8}
@media (prefers-color-scheme: light){:root{--bg:#f4f6fb;--card:#fff;--ink:#0b1020;--muted:#5b6482;--accent:#0f766e;--accent2:#4f46e5}}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
main{max-width:980px;margin:0 auto;padding:32px 20px}
h1{font-size:1.6rem;margin:0 0 4px}p.sub{color:var(--muted);margin:0 0 24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
.card{background:var(--card);border-radius:16px;padding:18px;border:1px solid rgba(128,140,200,.18)}
.k{color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.06em}
.v{font-size:2rem;font-weight:700;margin-top:6px;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent}
.bars{margin-top:18px}.row{display:flex;align-items:center;gap:10px;margin:8px 0}
.row span.l{width:150px;color:var(--muted);font-size:.9rem}
.bar{flex:1;background:rgba(128,140,200,.15);border-radius:99px;height:12px;overflow:hidden}
.bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:99px}
.note{color:var(--muted);font-size:.8rem;margin-top:18px}
</style></head><body><main>
<h1>Wayfin Compass: Support Impact</h1>
<p class="sub">Live numbers from conversations handled by the AI agent.</p>
<section class="grid" aria-label="Key metrics">
<div class="card"><div class="k">Cases handled</div><div class="v" id="total">0</div></div>
<div class="card"><div class="k">Self-service rate</div><div class="v" id="rate">0%</div></div>
<div class="card"><div class="k">Customer satisfaction</div><div class="v" id="csat">n/a</div></div>
<div class="card"><div class="k">Agent minutes saved (est.)</div><div class="v" id="mins">0</div></div>
</section>
<section class="card bars" aria-label="Cases by type"><div class="k">Cases by type</div><div id="bars"></div></section>
<p class="note" id="note"></p>
<script>
async function load(){
  const r = await fetch('/metrics'); const m = await r.json();
  document.getElementById('total').textContent = m.cases_total;
  document.getElementById('rate').textContent = m.self_service_rate_pct + '%';
  document.getElementById('csat').textContent = m.csat_average === null ? 'n/a' : m.csat_average + ' / 5';
  document.getElementById('mins').textContent = m.estimated_agent_minutes_saved;
  document.getElementById('note').textContent = m.assumptions_note;
  const box = document.getElementById('bars'); box.textContent = '';
  const max = Math.max(1, ...Object.values(m.cases_by_type));
  for (const [t, n] of Object.entries(m.cases_by_type)) {
    const row = document.createElement('div'); row.className = 'row';
    const l = document.createElement('span'); l.className = 'l'; l.textContent = t.replace('_',' ') + ' (' + n + ')';
    const b = document.createElement('div'); b.className = 'bar';
    const i = document.createElement('i'); i.style.width = (100*n/max) + '%';
    b.appendChild(i); row.appendChild(l); row.appendChild(b); box.appendChild(row);
  }
}
load(); setInterval(load, 5000);
</script></main></body></html>"""


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    return DASHBOARD_HTML


@app.get("/health")
def health() -> dict:
    return {"ok": True, "version": app.version}
