# Setup Guide: from this repo to a published eGain agent

> This guide was written without access to the eGain console, so menu names may differ slightly. Use the hackathon's Resources tab and eGain's own tutorial for exact clicks. The content in this repo is what you paste or upload.

## Step 1: Get access (10 min)
1. On Devpost, click **Join hackathon**.
2. Open the **Resources** tab and follow the eGain sign-up or tutorial link.

## Step 2: Knowledge-based agent (30 min)
1. Create a new AI Agent named **Wayfin Compass**.
2. Add the five files in `knowledge/` as the knowledge source (upload, or paste each as an article).
3. Set the agent language to **English** to match the content.
4. Let eGain generate intents, then **review them** against `agent-config/02-intents.md`. Rename, merge, and add example phrases.
5. Use *Test AI Agent* to ask questions from section A of `testing/test-plan.md`.

## Step 3: Pre-chat (10 min)
Create the form from `agent-config/01-pre-chat-form.md`. Map the "reply style" answer so it can steer responses.

## Step 4: Workflows (60 to 90 min)
Build Workflows A to F and the global rules from `agent-config/03-workflows.md`. If time is short, build A, D, and F first, then B, C, and E. Attach each to its workflow intent. Keep button labels exactly as written so testing is easy.

## Step 5: Deploy the actions API (20 min)
Option 1: Render (free)
1. Push this repo to GitHub.
2. In Render, create a **Web Service** from the repo. It reads `mock-api/render.yaml`.
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
In eGain, enable **Actions** and add the seven endpoints from `agent-config/04-actions.md`, using `mock-api/openapi.json` for field names. Connect each action to the matching workflow step.

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
