# Workflows

Four guided flows. Each is tied to a workflow intent (see `02-intents.md`). In every step, use the **Simple & short** wording when the pre-chat style is Simple.

---

## Workflow A: Dispute Navigator

**Goal:** Work out the dispute type, check eligibility, list the evidence, open a case.

```
START
 |
 v
Q1. What happened? (buttons)
   [I don't recognize this charge]  -> type = UNAUTHORIZED
   [I was charged twice]            -> type = DUPLICATE
   [I never got what I paid for]    -> type = NOT_RECEIVED
   [Item was not as described]      -> type = NOT_AS_DESCRIBED
   [Wrong amount charged]           -> type = WRONG_AMOUNT
   [I cancelled but was charged]    -> type = CANCELLED_SUB
   [Something else]                 -> Workflow D (handoff)
 |
 v
Q2. When did the charge appear on your statement? (buttons)
   [Within 60 days]   -> continue
   [Over 60 days ago] -> explain exceptional review is possible but not promised;
                          offer: continue anyway / talk to a person
 |
 v
Q3. Merchant name?            (free text, store as merchant)
Q4. Charge amount and currency? (free text, store as amount)
 |
 v
BRANCH by type
   UNAUTHORIZED:
      Q5. Do you still have your card? [Yes | No/lost]
          If No/lost -> run Workflow C first
          Else: strongly advise freezing the card in the app
      Note: provisional credit up to USD 1,000 within 5 business days
   DUPLICATE:
      Q5. Is one of the charges still "pending"? [Yes | No]
          Yes -> advise waiting up to 7 days; offer a reminder; end or continue
   NOT_RECEIVED / NOT_AS_DESCRIBED:
      Q5. Have you contacted the merchant? [Yes | No]
          No -> suggest doing so first; offer to open the case anyway
   WRONG_AMOUNT / CANCELLED_SUB:
      Q5. Do you have the receipt or cancellation confirmation? [Yes | No]
 |
 v
EVIDENCE CHECKLIST (from knowledge/02, for the chosen type)
 |
 v
Summarise: type, merchant, amount, deadline status. Ask: "Shall I open this case?"
   [Yes] -> ACTION: open_dispute_case
   [No]  -> offer to save the checklist / talk to a person
 |
 v
Confirm: case number WF-D-######, expected timeline (30 days; up to 90),
         email confirmation sent to the pre-chat email.
 |
 v
"Anything else?" -> END
```

**Error handling:** If the action fails, apologise, give the two contact options, and attach the handoff summary.

---

## Workflow B: Flight Disruption Check

**Goal:** Tell the customer what Wayfin Travel Cover and (as general information) airline rules may offer, then file a claim.

```
START
 |
 v
Q1. What happened? [Delayed | Cancelled | Bag delayed]
Q2. Did you pay for the flight or trip with your Wayfin card? [Yes | No | Not sure]
      No -> Wayfin cover does not apply. Give airline-rights info only (Q4), then offer a person.
      Not sure -> advise checking the receipt; continue with airline-rights info.
 |
 v
Q3. How long was the delay (at arrival, if known)? [Under 3h | 3 to 4h | 4 to 6h | Over 6h | Cancelled]
 |
 v
Q4. Where did the flight depart and arrive? [EU/UK involved | US involved | Elsewhere]
 |
 v
RESULT SCREEN (built from knowledge/03)
   Wayfin cover:
     Delay >= 4h      -> meals up to USD 75/day (receipts)
     Cancelled        -> prepaid trip costs up to USD 1,500
     Bag >= 6h        -> essentials up to USD 200
   Airline rules (general info only):
     EU/UK + arrival delay >= 3h or short-notice cancellation -> may be owed fixed compensation
        unless extraordinary circumstances. Distance bands: EUR 250 / 400 / 600.
     US + cancellation or significant change -> automatic refund right
     Elsewhere -> check the national aviation authority
   Always add: "This is general information, not legal advice."
 |
 v
Q5. Do you want to file a Wayfin claim now? [Yes | No]
   Yes -> collect: flight number, date, airline, expenses amount
          -> ACTION: file_flight_claim
   No  -> show document checklist, 30-day deadline
 |
 v
Confirm: case number WF-F-######, documents to upload by email, 30-day deadline.
 |
 v
END
```

---

## Workflow C: Urgent Card Safety

**Goal:** Protect the customer first, paperwork second.

```
START
 |
 v
Say: "First, freeze your card now: open the Wayfin app > Card > Freeze."
 |
 v
Q1. Has anyone used the card without your permission? [Yes | No | Not sure]
   Yes/Not sure -> offer Workflow A (UNAUTHORIZED) and show the phone line
   No           -> offer a replacement card (5 to 7 business days; express USD 15)
 |
 v
ACTION: order_replacement_card (if the customer agrees)
 |
 v
END
```

---

## Workflow D: Human Handoff

**Goal:** Pass the customer to a person with context, offering two or more contact options.

```
START
 |
 v
Offer choices: [Phone] [Email] [Request a callback]
 |
 v
Show the chosen option's details (from knowledge/05)
Show the handoff summary the person will receive (name, issue, details, what was said)
 |
 v
Ask: "Does this summary look right?" -> allow correction
 |
 v
ACTION (optional): create_handoff_ticket
 |
 v
END
```
