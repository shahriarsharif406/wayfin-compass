# Pre-Chat Workflow

Collected **before** the customer reaches the AI agent. The answers are passed into the conversation so Compass never asks for them again.

| # | Field | Type | Required | Notes |
|---|---|---|---|---|
| 1 | Name | Text | Yes | Used to greet the customer |
| 2 | Email | Email | Yes | Used for the case confirmation (demo address is fine) |
| 3 | What do you need help with? | Dropdown | Yes | Options below |
| 4 | Is this urgent right now? | Yes / No | Yes | Yes = stranded, card stolen, or money needed today. Drives priority routing (P1) |
| 5 | How would you like replies? | Choice | Yes | Standard, or Simple & short |
| 6 | Card last 4 digits | Text (4 digits) | No | Demo only. Placeholder: "Last 4 only. Use 0000 for the demo." Never the full number |
| 7 | I understand I am chatting with an AI assistant and agree to the privacy notice | Checkbox | Yes | AI disclosure and consent (see `docs/security-and-responsible-ai.md`) |

## Dropdown options for field 3
- A charge I do not recognize or that looks wrong (Card dispute)
- My flight was delayed or cancelled (Flight problem)
- I lost my card or it was stolen (Urgent card safety)
- Check on an existing case (Case status)
- A question about my card (General)
- Something else / talk to a person

## Choice options for field 5
- **Standard**: normal answers with full detail.
- **Simple & short**: short sentences, small steps, no jargon (uses `knowledge/04-plain-language-guide.md`).

## Privacy notice text (shown next to the checkbox)
"Compass is an AI assistant. It only uses the details you type here to help with your request. Please never type your full card number, PIN, CVV, or passwords. You can ask for a person at any time."

## How the answers are used
- Field 3 routes the opening: dispute, flight, safety, status, or general intent.
- Field 4 sets the priority: "Yes" opens P1 handling and shows the phone line first.
- Field 5 decides the reply style for the whole conversation.
- Fields 1 and 2 pre-fill the action forms and the escalation summary.
