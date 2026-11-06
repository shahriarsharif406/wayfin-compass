# Pre-Chat Workflow

Collected **before** the customer reaches the AI agent. The answers are passed into the conversation so Compass never asks for them again.

| # | Field | Type | Required | Notes |
|---|---|---|---|---|
| 1 | Name | Text | Yes | Used to greet the customer |
| 2 | Email | Email | Yes | Used for the case confirmation (demo address is fine) |
| 3 | What do you need help with? | Dropdown | Yes | Options below |
| 4 | How would you like replies? | Choice | Yes | Standard, or Simple & short |
| 5 | Card last 4 digits | Text (4 digits) | No | Demo only. Placeholder text says "Use 0000 for the demo" |

## Dropdown options for field 3
- A charge I do not recognize or that looks wrong (Card dispute)
- My flight was delayed or cancelled (Flight problem)
- A question about my card (General)
- Something else / talk to a person

## Choice options for field 4
- **Standard**: normal answers with full detail.
- **Simple & short**: short sentences, small steps, no jargon (uses `knowledge/04-plain-language-guide.md`).

## How the answers are used
- Field 3 routes the opening: dispute, flight, or general intent.
- Field 4 decides the reply style for the whole conversation.
- Fields 1 and 2 pre-fill the action forms and the escalation summary.
