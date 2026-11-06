# Test Plan

The hackathon requires testing the agent and **every workflow path**, both in **Test AI Agent** and through the **published demo link**. Published changes can take up to **5 minutes** to appear, so wait before re-testing.

Mark each row in both columns. Fix and re-test anything that fails.

## A. Knowledge accuracy (ask in your own words)
| # | Question | Expected answer | Test tool | Demo link |
|---|---|---|---|---|
| A1 | How long do I have to dispute a charge? | 60 days from statement date | [ ] | [ ] |
| A2 | What proof do I need for a duplicate charge? | Both charge dates and amounts, merchant, receipt showing one purchase | [ ] | [ ] |
| A3 | How long does a dispute take? | Up to 30 days; up to 90 for merchants outside the region | [ ] | [ ] |
| A4 | What if my flight is 5 hours late? | Meals up to USD 75/day with receipts (if paid with the card) | [ ] | [ ] |
| A5 | What is the ATM fee? | Free up to USD 400/month, then USD 2 | [ ] | [ ] |
| A6 | Can I dispute because I changed my mind? | No, not covered | [ ] | [ ] |
| A7 | How fast is express card replacement? | 2 to 3 business days, USD 15 | [ ] | [ ] |

## B. Knowledge gap (must NOT guess)
| # | Question | Expected behaviour | Test tool | Demo link |
|---|---|---|---|---|
| B1 | What is the weather in Paris? | Says it has no reliable answer, offers a person | [ ] | [ ] |
| B2 | Can I get a loan from Wayfin? | Says it is not in the help content, offers a person | [ ] | [ ] |
| B3 | What is my current balance? | Explains the demo cannot see real accounts | [ ] | [ ] |

## C. Pre-chat
| # | Check | Test tool | Demo link |
|---|---|---|---|
| C1 | Required fields block submission when empty | [ ] | [ ] |
| C2 | Chosen issue type sets the opening message | [ ] | [ ] |
| C3 | Name is used in the greeting; email is not asked again | [ ] | [ ] |
| C4 | Standard vs Simple & short changes reply length and wording | [ ] | [ ] |

## D. Workflow A: Dispute Navigator (every branch)
| # | Path | Expected | Test tool | Demo link |
|---|---|---|---|---|
| D1 | Unauthorized, has card, within 60 days | Freeze advice, provisional credit note, case WF-D-###### | [ ] | [ ] |
| D2 | Unauthorized, card lost | Runs Workflow C first | [ ] | [ ] |
| D3 | Duplicate, one still pending | Advises waiting 7 days | [ ] | [ ] |
| D4 | Duplicate, both posted | Evidence checklist, case opened | [ ] | [ ] |
| D5 | Not received, not contacted merchant | Suggests contacting merchant, offers to continue | [ ] | [ ] |
| D6 | Not as described | Checklist includes photos | [ ] | [ ] |
| D7 | Wrong amount | Asks for the receipt | [ ] | [ ] |
| D8 | Cancelled subscription | Asks for cancellation confirmation | [ ] | [ ] |
| D9 | Over 60 days | Explains manual review, no promise | [ ] | [ ] |
| D10 | "Something else" | Goes to Human Handoff | [ ] | [ ] |
| D11 | Customer declines to open the case | Offers checklist or a person, no action taken | [ ] | [ ] |

## E. Workflow B: Flight Disruption Check (every branch)
| # | Path | Expected | Test tool | Demo link |
|---|---|---|---|---|
| E1 | Delayed 4 to 6h, paid with card, EU/UK | Cover for meals, plus airline compensation info (general) | [ ] | [ ] |
| E2 | Cancelled, paid with card, US | Trip cost cover, automatic refund info | [ ] | [ ] |
| E3 | Bag delayed over 6h | Essentials up to USD 200 | [ ] | [ ] |
| E4 | Not paid with Wayfin card | No Wayfin cover; airline info only | [ ] | [ ] |
| E5 | Under 3h delay | Explains no standard cover | [ ] | [ ] |
| E6 | File claim: Yes | Case WF-F-######, 30-day deadline, documents list | [ ] | [ ] |
| E7 | File claim: No | Document checklist shown | [ ] | [ ] |

## F. Workflow C and D
| # | Path | Expected | Test tool | Demo link |
|---|---|---|---|---|
| F1 | "I lost my card" | Freeze first, then replacement offer | [ ] | [ ] |
| F2 | Replacement standard / express | Correct days and fee, request WF-R-###### | [ ] | [ ] |
| F3 | "Person please" at any point | Two or more contact options plus summary | [ ] | [ ] |
| F4 | Summary correction | Customer can fix details before handoff | [ ] | [ ] |

## G. Actions and failure handling
| # | Check | Test tool | Demo link |
|---|---|---|---|
| G1 | Each action returns a real case number | [ ] | [ ] |
| G2 | `get_case_status` finds the case number from G1 | [ ] | [ ] |
| G3 | With the API stopped, Compass falls back to handoff | [ ] | [ ] |

## Sign-off
- [ ] All rows pass in Test AI Agent
- [ ] All rows pass on the published demo link (waited 5 minutes after the last publish)
- [ ] Demo link opens in a private browser window
