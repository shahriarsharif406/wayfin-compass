# Workflows

Six guided flows. Each is tied to a workflow intent (see `02-intents.md`). In every step, use the **Simple & short** wording when the pre-chat style is Simple.

## Global rules (apply in every workflow)
1. **AI disclosure:** the first message says Compass is an AI assistant and a person is always available.
2. **Safety first:** if the pre-chat answer "Is this urgent right now?" is Yes, or the customer says stolen, stranded, scam, or hacked, show the phone line and offer Workflow D with priority **before** asking anything else.
3. **Sensitive data:** never ask for full card numbers, PIN, CVV, or passwords. If the customer types them, do not repeat them, and ask them to share only the last 4 digits.
4. **Idempotent actions:** every action call includes an `Idempotency-Key` so retries never create duplicate cases.
5. **Fewer questions:** never ask for something already given in the pre-chat form.
6. **After every completed workflow:** offer Workflow F (one-tap rating), then "Anything else?".
7. **Failure rule:** if an action fails, apologise once, show the two contact options, and attach the handoff summary.

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

---

## Workflow E: Case Status

**Goal:** Let a customer check an existing case in seconds, without calling.

```
START
 |
 v
Q1. What is your case number? (format WF-D-######, WF-F-######, WF-R-######, WF-H-######)
   Not sure -> explain it is in the confirmation email; offer Workflow D
 |
 v
ACTION: get_case_status(case_id)
   Not found -> check the format once; if still not found, offer Workflow D
 |
 v
Show: type, current status, priority, timeline (received date), next steps
   status = needs_manual_review -> explain a specialist is reviewing; do not promise an outcome
 |
 v
"Would you like to add a document checklist or talk to a person?" -> END or Workflow D
```

---

## Workflow F: Feedback (CSAT)

**Goal:** Measure satisfaction and AI resolution, and feed the business dashboard.

```
START
 |
 v
Q1. How was this chat? [1 Poor] [2] [3] [4] [5 Great]
Q2. Did Compass solve it without needing a person? [Yes | No]
Q3. (only if rating is 1 to 3) What could be better? (optional free text)
 |
 v
ACTION: submit_feedback
 |
 v
Thank the customer. If rating is 1 or 2, offer Workflow D. END
```
