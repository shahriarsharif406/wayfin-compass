# Wayfin Compass

**An AI support agent that walks travellers through card disputes and flight disruptions, built for the eGain hackathon "Build, Demo, and Take Home a Working AI Support Bot".**

Wayfin is a fictional travel-card company. Compass is its support assistant.

## What makes it different
Most hackathon bots answer FAQs. Compass is built around **guided workflows that end in a real action**, with the safeguards and metrics a real support team needs.

| Area | Feature |
|---|---|
| Knowledge | Answers only from Wayfin's own content and says so when it does not know |
| Pre-chat | Issue type, **urgency**, reply style, and an **AI disclosure and consent** checkbox |
| Accessibility | **Simple & short mode**: short sentences, small steps, no jargon |
| Dispute Navigator | Finds the type, lists the exact evidence, checks the 60-day window, opens a case |
| Flight Disruption Check | Card travel cover plus general airline-rights information, then files a claim |
| Urgent Card Safety | Freeze first, paperwork second |
| Case Status | Customers check progress, timeline, and next steps themselves |
| Priority handoff | P1/P2/P3 routing with response targets; phone, email, or callback; summary travels with the customer |
| Feedback | One-tap CSAT and "solved without a person" signal |
| Safety | Refuses full card numbers, resists prompt injection, honest about limits |
| Exact amounts | Airline compensation is calculated by tested code, never guessed by the model |
| Modern API | Idempotency keys, optional API-key auth, strict validation, confirmation-email previews |
| Evidence from space | Checks NASA satellite events and NOAA space weather near the airports on the flight date, as context for "extraordinary circumstances" (read-only, never changes the verdict) |
| Business view | Live `/dashboard` with self-service rate, CSAT, and agent time saved |

## Repo map
```
knowledge/      Content to train the agent (5 files, all fictional policy)
agent-config/   Pre-chat form, intents, 6 workflows, actions, persona
mock-api/       FastAPI actions service with dashboard (24 automated tests)
docs/           Architecture, security and responsible AI, business case, related open-source work
eval/           Golden question set and answer scorer
testing/        Full test plan for every workflow path
submission/     150-word description, demo video script, Devpost checklist
SETUP-GUIDE.md  Step-by-step plan to build and publish in eGain
.github/        CI that runs the API tests on every push
```

## Run the actions API locally
```bash
cd mock-api
pip install -r requirements.txt
pytest -q                  # 24 tests
uvicorn app:app --reload   # docs: /docs   dashboard: /dashboard   metrics: /metrics
```

## Notes
- Everything about Wayfin is invented for demonstration. Contact details use reserved example domains and numbers.
- Airline-rights text is a simplified general summary, not legal advice. Verify against official sources.
- Business-case numbers are illustrative assumptions, not measured results.
- No real customer or card data is used or stored.

## License
MIT
