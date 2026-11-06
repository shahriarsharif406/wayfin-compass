# Wayfin Compass

**An AI support agent that walks travellers through card disputes and flight disruptions, built for the eGain hackathon "Build, Demo, and Take Home a Working AI Support Bot".**

Wayfin is a fictional travel-card company. Compass is its support assistant.

## What makes it different
Most hackathon bots answer FAQs. Compass is built around **guided workflows that end in a real action**:

| Feature | What it does |
|---|---|
| Knowledge-based agent | Answers only from Wayfin's own content, and says so when it does not know |
| Pre-chat form | Captures the issue and a reply style before the chat starts |
| Simple & short mode | Short sentences and small steps for people who struggle with dense text |
| Dispute Navigator | Finds the dispute type, checks the 60-day window, lists the evidence, opens a case |
| Flight Disruption Check | Shows card travel cover and general airline-rights information, then files a claim |
| Urgent Card Safety | Freeze first, paperwork second |
| Human handoff | Phone, email, or callback, with a summary so customers never repeat themselves |
| Real actions | A small API creates case numbers (WF-D, WF-F, WF-R, WF-H) |

## Repo map
```
knowledge/      Content to train the agent (5 files, all fictional policy)
agent-config/   Pre-chat form, intents, workflows, actions, persona
mock-api/       FastAPI service the agent calls for actions (tested)
testing/        Full test plan for every workflow path
submission/     150-word description, demo video script, Devpost checklist
SETUP-GUIDE.md  Step-by-step plan to build and publish in eGain
```

## Run the actions API locally
```bash
cd mock-api
pip install -r requirements.txt
pytest
uvicorn app:app --reload   # docs at http://127.0.0.1:8000/docs
```

## Notes
- Everything about Wayfin is invented for demonstration. Contact details use reserved example domains and numbers.
- Airline-rights text is a simplified general summary, not legal advice.
- No real customer or card data is used or stored.

## License
MIT
