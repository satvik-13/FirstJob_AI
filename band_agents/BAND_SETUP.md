# Band Setup Guide for FirstJob AI
## Do this ONCE before running agents

---

## Step 1 — Create Band Account & Activate Pro

1. Go to https://app.band.ai → Sign up
2. Go to **Manage Billing** → Subscribe to Pro
3. Click **Add promotion code** → enter `BANDHACK26` → Apply
4. Add card to activate (free for 1 month)

---

## Step 2 — Create 6 Remote Agents on Band

Go to https://app.band.ai → **Agents** → **New Agent** → **Remote Agent**

Create all 6 with these exact names and descriptions:

| # | Name | Description |
|---|------|-------------|
| 1 | `FirstJob - Profile Agent` | Parses candidate resumes and summarizes skills, experience, and career preferences for downstream agents |
| 2 | `FirstJob - Job Scraper Agent` | Fetches and scores job listings from multiple platforms based on candidate profile |
| 3 | `FirstJob - Resume Tailor Agent` | Intelligently rewrites resume bullets for specific job descriptions without fabricating experience |
| 4 | `FirstJob - Apply Agent` | Coordinates the full application pipeline — tailoring, submission, and handoff to outreach |
| 5 | `FirstJob - Outreach Agent` | Finds hiring managers and sends personalized cold emails after each application |
| 6 | `FirstJob - Tracker Agent` | Logs all application events, maintains status records, and generates progress summaries |

**For EACH agent:**
- After creation, a popup shows the **API Key** → copy it immediately
- Go to agent settings → copy the **Agent UUID** (bottom right)

---

## Step 3 — Fill in agent_config.yaml

Open `band_agents/agent_config.yaml` and replace all placeholders:

```yaml
profile_agent:
  agent_id: "paste-uuid-here"
  api_key: "paste-api-key-here"

job_scraper_agent:
  agent_id: "paste-uuid-here"
  api_key: "paste-api-key-here"

# ... and so on for all 6
```

---

## Step 4 — Configure .env

Open `band_agents/.env` and fill in:

```env
THENVOI_REST_URL=https://app.band.ai/
THENVOI_WS_URL=wss://app.band.ai/api/v1/socket/websocket
ANTHROPIC_API_KEY=sk-ant-your-key-here
FIRSTJOB_API_URL=http://localhost:8000/api
FIRSTJOB_SERVICE_TOKEN=any-random-string-you-choose
```

---

## Step 5 — Install Band SDK

```bash
cd band_agents
pip install "band-sdk[anthropic]" python-dotenv pyyaml httpx loguru
```

---

## Step 6 — Verify ONE agent connects

Test with just the Profile Agent first:

```bash
cd band_agents
python profile_agent_band.py
```

You should see:
```
INFO: 🟢 Profile Agent connected to Band. Waiting for resume data...
```

If you see this, the setup is working. Ctrl+C to stop.

---

## Step 7 — Create the Band Workflow Room

1. Go to https://app.band.ai → **Rooms** → **New Room**
2. Name it: `FirstJob Workflow`
3. Add all 6 agents as participants (under **Remote** section)
4. Add yourself as a participant too

---

## Step 8 — Start all agents

```bash
cd band_agents
bash start_agents.sh
```

---

## Step 9 — Test the full pipeline

In the `FirstJob Workflow` Band room, send:

```
@ProfileAgent New candidate: [Your Name]
Skills: Python, React, SQL
Experience: 1 internship at startup
Domain: Software Engineering
Location: Bangalore
```

You should see all 6 agents collaborate in the room:
1. Profile Agent summarizes the profile
2. Job Scraper finds and scores matching jobs
3. (Select a job) Apply Agent kicks off
4. Resume Tailor shows what it changed
5. Apply Agent submits and confirms
6. Outreach Agent sends the cold email
7. Tracker Agent logs everything

---

## Troubleshooting

**Agent won't connect:**
- Check THENVOI_WS_URL is exactly `wss://app.band.ai/api/v1/socket/websocket`
- Check the agent UUID matches what's on Band platform
- Make sure the API key is from that specific agent (not your account key)

**Agent connects but doesn't respond:**
- Make sure the agent is added to the room
- Use `@AgentName` to mention it — agents only respond to mentions

**"Agent not found" error:**
- The agent UUID in agent_config.yaml doesn't match Band platform
- Recreate the agent on Band and copy the new UUID

---

## What judges will see

When you demo, open the `FirstJob Workflow` room on Band.
They'll see all 6 agents collaborating in real time:
- Task handoffs via @mentions
- Structured outputs from each agent
- Clear role specialization
- The full audit trail of the pipeline

This is exactly what the judging criteria ask for:
✅ Clear task handoffs
✅ Shared context
✅ Role specialization  
✅ Task state visible across agents
