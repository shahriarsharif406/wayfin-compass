# Setup Guide: from this repo to a published eGain agent

> This guide was written without access to the eGain console, so menu names may differ slightly. Use the hackathon's Resources tab and eGain's own tutorial for exact clicks. The content in this repo is what you paste or upload.

## Step 0: Official eGain facts (confirmed from eGain's hackathon page)
- Participation is described as **limited and first-come, first-served**, so sign up early.
- Official hackathon page: https://www.egain.com/ai-agent-hackathon/
- **Submit here as well:** https://www.egain.com/ai-agent-hackathon-project-submission/ (also submit on Devpost).
- Hands-on lab: https://share.articulate.com/daJ5S2RJxBQWPP_ijlVud
- Challenge Discord: https://discord.gg/J7t4nk3QK
- Judging is out of **125 points**: customer and business value 25, functionality and reliability 25, effective use of eGain 20, creativity and customer experience 15, **action and good judgment 25**, **demo video and storytelling 15**. Ties are broken by functionality, then video, then business value.
- Each person may join only **one** submission. Teams of up to 3.
- Use only authorized content with no real personal data. Disclose templates, code, and third-party assets. Generative AI tools are allowed.

## Step 1: Get access (10 min)
1. On Devpost, click **Join hackathon**.
2. Create a free trial account at https://www.egain.com/try-ai-agent/ (AI Agent for Customer Self-Service) with a working email. Reported limits: 5 AI agents, 10M characters per agent, content from PDF, Word, or HTML files, websites, or a knowledge portal, escalation by SMS, email, or phone.
3. Do the hands-on lab above once to learn the screens.
4. eGain's help pages: Create AI Agent, Configure Data Source, Test AI Agent, Personalize, Configure Workflows, Enable Actions, Create External Credentials, all under https://help.egain.com/help/ai_agent_css/welcome.htm

## Step 2: Knowledge-based agent (30 min)
1. Create a new AI Agent named **Wayfin Compass**.
2. Upload the five Word files in `knowledge/upload-ready/` as the data source (eGain accepts PDF, Word, and HTML, not Markdown).
3. Set the agent language to **English** to match the content.
4. Let eGain generate intents, then **review them** against `agent-config/02-intents.md`. Rename, merge, and add example phrases.
5. Use *Test AI Agent* to ask questions from section A of `testing/test-plan.md`.

### Optional accelerator: eGain's official MCP server
If your eGain tenant has AI Services enabled and a client app with the read permissions, the open-source [eGain MCP server](https://github.com/eGain/egain-mcp-server) (MIT) lets Claude search your portal and call `get-best-answer`. You can use it to ask the questions in `eval/golden_questions.yaml` quickly and score them with `python eval/score_answers.py answers.csv`. It also has optional authoring tools (off by default) for creating articles. Never paste access tokens into chats or commit them to GitHub. Skip this if your hackathon access does not include API credentials.

## Step 3: Pre-chat (10 min)
Create the form from `agent-config/01-pre-chat-form.md`. Map the "reply style" answer so it can steer responses.

## Step 4: Workflows (60 to 90 min)
Build Workflows A to F and the global rules from `agent-config/03-workflows.md`. If time is short, build A, D, and F first, then B, C, and E. Attach each to its workflow intent. Keep button labels exactly as written so testing is easy.

## Step 5: Deploy the actions API (20 min)
Option 1: Render (free)
1. Push this repo to GitHub.
2. In Render, create a **Web Service** from the repo. It reads `render.yaml` at the repo root.
3. Open `https://YOUR-SERVICE.onrender.com/docs` to confirm the API is live.
4. Free instances sleep when idle, so open `/health` a minute before recording or judging.
5. (Recommended) In Render's Environment settings add `WAYFIN_API_KEY` with a long random value, then add the header `X-API-Key` with the same value in the eGain action settings. Do not commit the key to GitHub.
6. Open `/dashboard` to see the live business metrics page. It is useful as a screenshot for Devpost.

Option 3: Docker
```bash
cd mock-api
docker build -t wayfin-compass-api .
docker run -p 8000:8000 -e WAYFIN_API_KEY=change-me wayfin-compass-api
```

Option 2: Run locally for development
```bash
cd mock-api
pip install -r requirements.txt
uvicorn app:app --reload
pytest
```

## Step 6: Register actions (30 min)
In eGain, enable **Actions** (help page "Enable Actions"), store the API key under **External Credentials** (help page "Create External Credentials"), and add the seven endpoints from `agent-config/04-actions.md`, using `mock-api/openapi.json` for field names. Connect each action to the matching workflow step.

## Step 7: Escalation (10 min)
Add Phone, Email, and Callback options using `knowledge/05-contact-and-escalation.md`. Include the handoff summary.

## Step 8: Personalize and publish (20 min)
Apply the name, greeting, and tone from `agent-config/05-persona-and-tone.md`, set a logo and colors, and **publish**. Wait up to 5 minutes.

## Step 9: Test everything (60 min)
Walk through `testing/test-plan.md` in both Test AI Agent and the published demo link.

## Step 10: Record and submit
Use `submission/demo-video-script.md` and `submission/devpost-checklist.md`.

## Time plan (about 4 days of part-time work)
| Day | Work |
|---|---|
| Day 1 | Steps 1 to 3 |
| Day 2 | Steps 4 to 5 |
| Day 3 | Steps 6 to 8 |
| Day 4 | Step 9, then record |
| Day 5 | Buffer, polish, submit early |
