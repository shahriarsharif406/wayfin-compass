# Actions (the agent acts for the customer)

The hackathon asks that the agent can take a **real action**. Compass does this by calling the web service in `mock-api/`, which creates a case, returns a case number, a priority, and next steps. Deploy it publicly (see `SETUP-GUIDE.md`) and register the endpoints below as actions in eGain.

Contract file: `mock-api/openapi.json` (also live at `/docs` and `/openapi.json` on the running service).

| Action name | Method and path | Triggered from | Key inputs | Key outputs |
|---|---|---|---|---|
| `open_dispute_case` | `POST /disputes` | Workflow A | name, email, dispute_type, merchant, amount, currency, statement_within_60_days, urgent, card_last4 (optional) | `case_id` (WF-D-######), `status`, `priority`, `provisional_credit_eligible`, `evidence_checklist`, `confirmation_email` |
| `file_flight_claim` | `POST /flight-claims` | Workflow B | name, email, issue, airline, flight_number, flight_date, expenses_amount, delay_hours, urgent | `case_id` (WF-F-######), `status`, `claim_deadline_days`, `documents_needed`, `max_cover_usd` |
| `order_replacement_card` | `POST /replacement-cards` | Workflow C | name, email, express | `request_id` (WF-R-######), `delivery_business_days`, `fee_usd` |
| `create_handoff_ticket` | `POST /handoff-tickets` | Workflow D | name, email, issue_type, summary, preferred_contact, urgent | `ticket_id` (WF-H-######), `priority` (P1/P2/P3), `target_response` |
| `get_case_status` | `GET /cases/{case_id}` | Workflow E | case_id | `status`, `priority`, `timeline`, `next_steps` |
| `get_evidence_checklist` | `GET /evidence-checklist/{dispute_type}` | Workflow A | dispute_type | `documents` |
| `estimate_airline_compensation` | `POST /airline-compensation/estimate` | Workflow B | distance_km, arrival_delay_minutes, cancelled, cancellation_notice_days, covered_route, intra_eu, reason | `verdict`, `indicative_amount_eur`, `reasons`, `disclaimer` |
| `submit_feedback` | `POST /feedback` | Workflow F | rating (1 to 5), case_id, resolved_without_human, comment | `ok` |

## Modern API behaviour to rely on
- **Idempotency:** send an `Idempotency-Key` header (for example the conversation ID plus the step name). If the customer taps "Open case" twice or eGain retries, the same case number is returned and no duplicate is created.
- **Authentication:** set the environment variable `WAYFIN_API_KEY` on the server and add the header `X-API-Key` in the eGain action settings. If the variable is not set, the demo API stays open.
- **Priority routing:** `P1` urgent or safety (phone within 15 minutes), `P2` high-risk or distressed (2 hours), `P3` standard (1 business day).
- **Card-number guard:** the API rejects free text that looks like a full card number (13 to 19 digits).
- **Confirmation email preview:** responses include a preview object. Nothing is sent in the demo; production would hand it to an email service.
- **Live business metrics:** `GET /metrics` and the page `GET /dashboard` show cases handled, self-service rate, CSAT, and estimated agent time saved.

## Why amounts come from code
The airline-compensation amount is calculated by a deterministic function, not by the language model. The agent reads the result back to the customer. This keeps euro figures exact and auditable, and the tests in `mock-api/test_app.py` lock the rules in.

## Design notes
- The service stores cases in memory (demo only). It never asks for or stores real card numbers.
- Business rules mirror the policy files: disputes outside the 60-day window return `needs_manual_review` instead of failing; unauthorized disputes up to USD 1,000 are flagged for provisional credit.
- If the service is unreachable, Compass must fall back to the Human Handoff workflow.
