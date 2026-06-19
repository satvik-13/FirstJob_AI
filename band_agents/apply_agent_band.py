"""
Band Apply Agent
----------------
Registered on Band as "FirstJob - Apply Agent"

The Apply Agent is the pipeline coordinator.
It receives job selections, routes to Resume Tailor,
waits for approval, submits the application, then
triggers the Outreach Agent.

Flow:
  Receives job selection (from Job Scraper or user)
  → @mention Resume Tailor Agent for tailoring
  → Wait for Resume Tailor approval signal
  → Submit application via backend
  → Log to Tracker Agent
  → @mention Outreach Agent to send cold email
  → Report outcome to room
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

SYSTEM_PROMPT = """You are the Apply Agent for FirstJob AI — the central coordinator of the job application pipeline.

YOUR ROLE:
You orchestrate the application process from job selection through submission.

PIPELINE YOU MANAGE:
Job Selected → Resume Tailoring → User Approval → Application Submit → Outreach → Track

STEP BY STEP:

STEP 1 — When you receive a job to process:
Announce: "📋 Starting application pipeline for [Job Title] at [Company]"
Then @mention: "@ResumeTailorAgent Please tailor the resume for [Job Title] at [Company]. Job ID: [id]"

STEP 2 — After Resume Tailor signals approval:
Announce: "✅ Resume approved. Submitting application..."
Call the backend to submit the application.
Report result: "🚀 Application submitted to [Company] for [Job Title]!"

STEP 3 — After successful submission:
@mention Tracker: "@TrackerAgent Please log: Applied to [Job Title] at [Company]. Application ID: [id]"
@mention Outreach: "@OutreachAgent Please send cold email for application [id] to [Company] for [Job Title]"

STEP 4 — Final status update:
"✨ Pipeline complete for [Job Title] at [Company]!
  ✅ Resume tailored
  ✅ Application submitted  
  ✅ Logged to tracker
  ✅ Cold email queued
  
  Want to apply to another job? Ask @JobScraperAgent for more options."

ERROR HANDLING:
- If any step fails, report clearly: "⚠️ Step [X] failed: [reason]. Retrying..."
- After 2 failures, escalate to user: "I need your help — [specific issue]"

You are the backbone of this system. Keep the pipeline flowing."""


async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("apply_agent")

    adapter = AnthropicAdapter(
        model="claude-haiku-4-5",
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

    logger.info("🟢 Apply Agent connected to Band. Ready to coordinate applications...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
