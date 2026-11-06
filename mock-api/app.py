"""Wayfin Compass: demo actions service.

A tiny in-memory API that lets the Compass AI agent take real actions
(open a dispute, file a flight claim, order a replacement card, create a
handoff ticket, look up a case). Demo only: no real card data is stored.
"""
from __future__ import annotations

import itertools
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(
    title="Wayfin Compass Actions API",
    description="Demo actions for the Wayfin Compass support agent.",
    version="1.0.0",
)

_counters = {
    "D": itertools.count(104827),
    "F": itertools.count(208315),
    "R": itertools.count(310442),
    "H": itertools.count(412096),
}
CASES: Dict[str, dict] = {}


def _new_id(kind: str) -> str:
    return f"WF-{kind}-{next(_counters[kind])}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _save(case_id: str, case_type: str, status: str, payload: dict) -> None:
    CASES[case_id] = {
        "case_id": case_id,
        "type": case_type,
        "status": status,
        "created_at": _now(),
        "details": payload,
    }


# ---------- Disputes ----------
class DisputeType(str, Enum):
    unauthorized = "unauthorized"
    duplicate = "duplicate"
    not_received = "not_received"
    not_as_described = "not_as_described"
    wrong_amount = "wrong_amount"
    cancelled_subscription = "cancelled_subscription"


class DisputeIn(BaseModel):
    name: str
    email: EmailStr
    dispute_type: DisputeType
    merchant: str
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3, description="ISO code, e.g. USD")
    statement_within_60_days: bool = True
    card_last4: Optional[str] = Field(default=None, pattern=r"^\d{4}$")


class DisputeOut(BaseModel):
    case_id: str
    status: str
    expected_resolution_days: int
    provisional_credit_eligible: bool
    message: str


@app.post("/disputes", response_model=DisputeOut)
def open_dispute(body: DisputeIn) -> DisputeOut:
    case_id = _new_id("D")
    if not body.statement_within_60_days:
        status = "needs_manual_review"
        message = (
            "The 60-day window has passed, so a specialist will review this case. "
            "Approval is not guaranteed."
        )
    else:
        status = "opened"
        message = "Case opened. A confirmation email is on its way."
    # Policy: provisional credit for unauthorized charges up to USD 1,000.
    provisional = (
        body.dispute_type == DisputeType.unauthorized
        and body.currency.upper() == "USD"
        and body.amount <= 1000
        and body.statement_within_60_days
    )
    _save(case_id, "dispute", status, body.model_dump(mode="json"))
    return DisputeOut(
        case_id=case_id,
        status=status,
        expected_resolution_days=30,
        provisional_credit_eligible=provisional,
        message=message,
    )


# ---------- Flight claims ----------
class FlightIssue(str, Enum):
    delay = "delay"
    cancellation = "cancellation"
    baggage = "baggage"


class FlightClaimIn(BaseModel):
    name: str
    email: EmailStr
    issue: FlightIssue
    airline: str
    flight_number: str
    flight_date: str = Field(description="YYYY-MM-DD")
    expenses_amount: float = Field(ge=0, description="USD")
    delay_hours: Optional[float] = Field(default=None, ge=0)


class FlightClaimOut(BaseModel):
    case_id: str
    status: str
    claim_deadline_days: int
    documents_needed: List[str]
    max_cover_usd: float
    message: str


COVER = {
    FlightIssue.delay: (75.0, "Meals and refreshments, up to USD 75 per day"),
    FlightIssue.cancellation: (1500.0, "Prepaid non-refundable trip costs, up to USD 1,500"),
    FlightIssue.baggage: (200.0, "Essential items, up to USD 200"),
}


@app.post("/flight-claims", response_model=FlightClaimOut)
def file_flight_claim(body: FlightClaimIn) -> FlightClaimOut:
    try:
        datetime.strptime(body.flight_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="flight_date must be YYYY-MM-DD")

    cap, cover_text = COVER[body.issue]
    status = "opened"
    message = f"Claim opened. Cover: {cover_text}."
    # Policy thresholds: delay >= 4h, baggage >= 6h.
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
    _save(case_id, "flight_claim", status, body.model_dump(mode="json"))
    return FlightClaimOut(
        case_id=case_id,
        status=status,
        claim_deadline_days=30,
        documents_needed=docs,
        max_cover_usd=cap,
        message=message,
    )


# ---------- Replacement card ----------
class ReplacementIn(BaseModel):
    name: str
    email: EmailStr
    express: bool = False


class ReplacementOut(BaseModel):
    request_id: str
    delivery_business_days: str
    fee_usd: float


@app.post("/replacement-cards", response_model=ReplacementOut)
def order_replacement(body: ReplacementIn) -> ReplacementOut:
    request_id = _new_id("R")
    _save(request_id, "replacement_card", "ordered", body.model_dump(mode="json"))
    if body.express:
        return ReplacementOut(request_id=request_id, delivery_business_days="2 to 3", fee_usd=15.0)
    return ReplacementOut(request_id=request_id, delivery_business_days="5 to 7", fee_usd=0.0)


# ---------- Handoff ----------
class HandoffIn(BaseModel):
    name: str
    email: EmailStr
    issue_type: str
    summary: str
    preferred_contact: str = Field(description="phone, email, or callback")


class HandoffOut(BaseModel):
    ticket_id: str
    status: str


@app.post("/handoff-tickets", response_model=HandoffOut)
def create_handoff(body: HandoffIn) -> HandoffOut:
    ticket_id = _new_id("H")
    _save(ticket_id, "handoff", "queued", body.model_dump(mode="json"))
    return HandoffOut(ticket_id=ticket_id, status="queued")


# ---------- Lookup ----------
@app.get("/cases/{case_id}")
def get_case(case_id: str) -> dict:
    case = CASES.get(case_id.upper())
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {k: case[k] for k in ("case_id", "type", "status", "created_at")}


@app.get("/health")
def health() -> dict:
    return {"ok": True}
