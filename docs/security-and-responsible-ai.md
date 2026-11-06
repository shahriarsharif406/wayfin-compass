# Security, Privacy, and Responsible AI

How Wayfin Compass is designed to be safe to put in front of real customers. Wayfin is fictional, but the controls below are the ones a production support agent in financial services needs.

## 1. Transparency
- The agent states it is an AI assistant in its first message and in the pre-chat consent line.
- A person is always one message away ("person please" at any time).
- The agent says clearly when it cannot see real account data.

## 2. Data minimisation and PCI-style hygiene
| Risk | Control |
|---|---|
| Customer types a full card number, PIN, CVV, or password | Safety intent refuses to repeat or use it and asks for the last 4 digits only |
| Free text reaching the case system | The API rejects text that looks like a 13 to 19 digit card number (tested) |
| Over-collecting personal data | Only name, email, and case details are collected, and only when needed |
| Stored data | Demo stores cases in memory only. Nothing persists after a restart |
| Logs and transcripts | Production should mask digits and emails before storage |

## 3. Grounded answers, no hallucinated policy
- Answers come only from the uploaded Wayfin content.
- Knowledge gaps produce an honest "I don't have that" and a handoff, never a guess.
- Airline-rights text is labelled general information, not legal advice, and never promises an outcome.

## 4. Prompt-injection and misuse resistance
- Requests to ignore rules, role-play as someone else, or reveal other customers' data are declined calmly (Manipulation attempt intent).
- Actions accept only validated, typed fields. Free text cannot change which action runs.
- Customers can only look up a case by its exact case number.

## 5. API security
- Optional `X-API-Key` authentication (set `WAYFIN_API_KEY` to enforce).
- Idempotency keys stop duplicate cases from retries.
- Strict input validation with length and range limits.
- **Production still needs:** TLS-only access, rate limiting, per-customer authorization (one-time passcode before status lookups), audit logs, and a real database.

## 6. Fairness and accessibility
- Simple & short mode supports people with cognitive or learning disabilities, second-language readers, and older adults.
- The dashboard and docs use accessible colour contrast and semantic HTML.
- Escalation always offers more than one channel (phone, email, callback) so people who cannot use one still have another.
- Priority routing (P1 to P3) is based on urgency and safety wording, not on who the customer is.

## 7. Human oversight
- Specialists receive a handoff summary so customers never repeat their story.
- Disputes outside policy go to manual review rather than being auto-declined.
- CSAT and "solved without a person" ratings show where the agent needs improvement.

## 8. Known limitations (honest list)
- The demo cannot verify identity or see real balances.
- Airline-rights summaries are simplified and should be verified against official sources.
- Metrics use illustrative time-saving assumptions, not measured data.
