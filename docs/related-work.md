# Related Open-Source Work

A GitHub search (Nov 2026) found **no open-source project that combines card disputes, flight-disruption claims, and guided support workflows on eGain**. The nearest projects solve parts of the problem. This page lists what they do, what Compass learned from them, and how Compass differs. Ideas were adapted; no code was copied.

| Project | License | What it does | What we took (as an idea) | How Compass differs |
|---|---|---|---|---|
| [eGain/egain-mcp-server](https://github.com/eGain/egain-mcp-server) | MIT | Official MCP server for eGain Knowledge: search, `get-best-answer`, `retrieve-chunks`, optional authoring tools | Use it to upload articles and to test answers automatically (see SETUP-GUIDE, optional step) | Compass is the support agent itself, with workflows and actions |
| [david-egri/agentic-rag-passenger-rights](https://github.com/david-egri/agentic-rag-passenger-rights) | MIT | Chatbot for EU flight-compensation rights with grounded retrieval and a deterministic calculator | **Amounts come from code, not the model**; a written evaluation set | Compass adds disputes, handoff, case actions, and a business dashboard |
| [saai-syvendra/hackerrank-orchestrate](https://github.com/saai-syvendra/hackerrank-orchestrate) | None stated | Winning support-triage agent: answer only from the corpus or escalate; handles prompt injection | Strict "answer or escalate" rule, injection test cases | Compass uses a no-code platform and adds real actions |
| [Alpha-Park/genpark-...-eu261-dispute-filer-skill](https://github.com/Alpha-Park/genpark-personal-agent-flight-compensation-eu261-dispute-filer-skill) | MIT | Small MCP tool that evaluates EU261 delay compensation | Cross-check of distance bands; the 3-4 hour long-haul reduction (EUR 300) | Compass also checks cancellation notice and the airline's stated reason |
| [Thaynabarreiro/amadeus-disruption-agent](https://github.com/Thaynabarreiro/amadeus-disruption-agent) | MIT | LangGraph agent for flight disruption on Amadeus APIs | Confirms demand for disruption assistants | Compass is card-linked and customer-support focused |
| [paveldevyatov/refund-anything-ai-prompt](https://github.com/paveldevyatov/refund-anything-ai-prompt) | MIT | Prompt and agent skill for getting refunds | Confirms demand for dispute help | Compass runs inside a company's support channel, not as a personal tool |

## What this changed in Compass
1. **Deterministic compensation estimator** (`POST /airline-compensation/estimate`) with tests, so euro amounts are never guessed.
2. **Long-haul reduction rule** added to the knowledge base (EUR 300 for a 3 to 4 hour arrival delay over 3,500 km).
3. **Golden question set** (`eval/golden_questions.yaml`) and a scorer (`eval/score_answers.py`) to test answer accuracy after upload.
4. **Adversarial cases** (card number in chat, "ignore your rules") added to the golden set.

## Caution
The GitHub projects above are community code of varying quality, and EU261 summaries in any of them should be verified against the official regulation text before relying on them.

## Data and ideas reused (second research pass)
| Source | What we took | License |
|---|---|---|
| [OurAirports data](https://github.com/davidmegginson/ourairports-data) | About 3,200 airports with scheduled service and IATA codes (name, coordinates), stored as `mock-api/airports.csv`, used to find satellite events near each airport | Public domain |
| NASA EONET (keyless API) | Satellite-observed storms, volcanoes, wildfires, floods and dust near an airport on the flight date | Open NASA data |
| NOAA SWPC (keyless JSON) | Planetary K-index for geomagnetic storm days | Open US government data |

## What we looked at and did not use (and why)
- **OpenSky Network / pyopensky / traffic:** ADS-B flight tracks are open for research, but the live API states it does not provide delay or schedule data, is non-commercial, and may block cloud hosts. Too fragile for a one-minute demo.
- **Commercial EU261 checkers (AirHelp and similar):** they apply the same distance and delay bands we do. None of those we found shows satellite or space-weather context for the "extraordinary circumstances" question, which is the gap Evidence from Space fills.
- **Space-weather aviation advisories (ICAO, NOAA SWPC):** real impact is mostly on polar and transoceanic HF radio and satellite navigation, so a high K-index is a weak signal on its own. We label it as context, never proof. A possible later step is reading the official ICAO advisory feed.
