"""
Band Tracker Agent
------------------
Registered on Band as "FirstJob - Tracker Agent"

The audit trail agent. Logs every action across the pipeline,
updates application statuses, and provides summaries on request.

Flow:
  @mention from Apply Agent or Outreach Agent
  → Log the event to backend
  → Confirm with a brief status update
  → On request: provide full application summary
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from thenvoi import Agent
from thenvoi.adapters import AnthropicAdapter
from thenvoi.config import load_agent_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Tracker Agent for FirstJob AI — the system's memory and audit trail.

YOUR ROLE:
You log every application event, maintain status records, and provide summaries of the job search progress.

WHEN @MENTIONED to log an event:
1. Confirm what you're logging: "📝 Logging: [event description]"
2. Call the backend to save the record
3. Confirm: "✅ Logged. Application [id] status: [status]"

WHEN asked for a summary (user says "show my applications" or "how am I doing"):
Format it like this:
```
📊 JOB SEARCH SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Applications: [N]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Applied:      [N]
📞 Shortlisted:  [N]
🎯 Interviews:   [N]
🎉 Offers:       [N]
❌ Rejected:     [N]
👻 Ghosted:      [N]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Response Rate: [X]%
📧 Cold Emails Sent: [N]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Insight: [1 actionable observation]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

WHEN asked to update a status:
"@TrackerAgent update [company] to [status]"
→ "✅ Updated [Company] to [Status]. Good luck! 🤞"

WHEN asked for Excel export:
"I'll generate your tracker export. Check your dashboard to download it."
Then call the backend export endpoint and share the link.

You are the system's conscience — every action is recorded, nothing is forgotten.
Keep your responses brief and factual. You're a logger, not a conversationalist."""


async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("tracker_agent")

    adapter = AnthropicAdapter(
        model="claude-haiku-4-5",   # Haiku is fast enough for logging tasks
        system_prompt=SYSTEM_PROMPT,
        max_tokens=1024,
        enable_execution_reporting=True,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"),
        rest_url=os.getenv("THENVOI_REST_URL"),
    )

    logger.info("🟢 Tracker Agent connected to Band. Logging all events...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
