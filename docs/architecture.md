# Architecture

```mermaid
flowchart LR
    C([Customer]) --> W[Published eGain chat link]
    W --> P[Pre-chat form<br/>consent, urgency, reply style]
    P --> A{Wayfin Compass<br/>AI Agent}
    K[(Knowledge base<br/>5 policy documents)] --> A
    A -->|workflow A to F| F[Guided workflows]
    F -->|actions| API[Actions API<br/>FastAPI]
    API --> S[(Cases, timeline,<br/>feedback)]
    API --> M[/metrics and /dashboard/]
    A -->|unsure or requested| H[Human handoff<br/>phone, email, callback<br/>with summary and priority]
```

## Request flow for a dispute
1. Customer completes the pre-chat form (issue, urgency, reply style, consent).
2. Compass greets by name, states it is an AI, and starts Workflow A.
3. The customer answers a few button questions; the agent shows the evidence checklist.
4. `POST /disputes` is called with an `Idempotency-Key`. The API returns the case number, priority, provisional-credit flag, and next steps.
5. Compass confirms, offers Workflow F (rating), and ends.
6. The business dashboard updates within seconds.

## Components
| Part | Role | Folder |
|---|---|---|
| Knowledge base | Source of truth for answers | `knowledge/` |
| Agent configuration | Intents, workflows, pre-chat, persona | `agent-config/` |
| Actions API | Creates cases, tracks status, collects feedback, reports metrics | `mock-api/` |
| Tests | 20 automated API tests and a manual agent test plan | `mock-api/test_app.py`, `testing/` |
| CI | Runs tests on every push | `.github/workflows/ci.yml` |
