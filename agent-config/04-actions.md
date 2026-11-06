# Actions (the agent acts for the customer)

The hackathon asks that the agent can take a **real action**. Compass does this by calling the small web service in `mock-api/`, which creates a case and returns a case number. Deploy it publicly (see `SETUP-GUIDE.md`) and register the endpoints below as actions in eGain.

Contract file: `mock-api/openapi.json` (can be exported from the running service at `/openapi.json`).

| Action name | Method and path | Triggered from | Inputs | Returns |
|---|---|---|---|---|
| `open_dispute_case` | `POST /disputes` | Workflow A | name, email, dispute_type, merchant, amount, currency, statement_within_60_days, card_last4 (optional) | `case_id` (WF-D-######), `status`, `expected_resolution_days`, `provisional_credit_eligible` |
| `file_flight_claim` | `POST /flight-claims` | Workflow B | name, email, issue (delay / cancellation / baggage), airline, flight_number, flight_date, expenses_amount | `case_id` (WF-F-######), `status`, `claim_deadline_days`, `documents_needed` |
| `order_replacement_card` | `POST /replacement-cards` | Workflow C | name, email, express (true/false) | `request_id` (WF-R-######), `delivery_business_days`, `fee_usd` |
| `create_handoff_ticket` | `POST /handoff-tickets` | Workflow D | name, email, issue_type, summary, preferred_contact | `ticket_id` (WF-H-######), `status` |
| `get_case_status` | `GET /cases/{case_id}` | Any workflow, "check my case" | case_id | `case_id`, `type`, `status`, `created_at` |

## Design notes
- The service stores cases in memory (demo only). It never asks for or stores real card numbers.
- Business rules in the service mirror the policy files: disputes outside the 60-day window return `status: "needs_manual_review"` instead of failing; unauthorized disputes up to USD 1,000 are flagged for provisional credit.
- If the service is unreachable, Compass must fall back to the Human Handoff workflow.
