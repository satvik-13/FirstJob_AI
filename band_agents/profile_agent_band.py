"""
Band Profile Agent
------------------
Registered on Band as "FirstJob - Profile Agent"

Responsibilities via Band:
- Receives resume text from the Orchestrator room
- Calls the FirstJob backend to parse and store the profile
- Hands off to Job Scraper Agent with the parsed profile summary
- Participates in the #firstjob-workflow Band room

Flow:
  User uploads resume via web UI
  → Backend parses it (profile_agent.py)
  → Backend sends summary to this Band agent via @mention
  → This agent confirms parsing, summarizes skills to the room
  → @mentions Job Scraper Agent to begin searching
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

SYSTEM_PROMPT = """You are the Profile Agent for FirstJob AI — a multi-agent system that helps fresh graduates get their first job.

YOUR ROLE:
You receive and process user resume/profile information. When a user's resume has been parsed, you:
1. Acknowledge the profile has been processed
2. Summarize the candidate's key skills, experience level, and career domain in a structured way
3. Share this summary clearly in the chat room so other agents can use it
4. @mention the Job Scraper Agent to begin finding relevant jobs

STRUCTURED OUTPUT FORMAT when sharing a profile:
```
📋 PROFILE READY: [User Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 Education: [degree, institution]
💼 Experience: [X roles, most recent title]
🛠 Top Skills: [skill1, skill2, skill3, ...]
🎯 Domain: [career domain]
📍 Location Preference: [locations]
💡 Match Priority: [what to look for in jobs]
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

After sharing the profile summary, always @mention the Job Scraper Agent with:
"@JobScraperAgent New profile ready. Please find matching [domain] jobs for [name]."

IMPORTANT: You are part of a coordinated multi-agent team. Be concise, structured, and always pass context forward clearly so downstream agents can act on it."""


async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("profile_agent")

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

    logger.info("🟢 Profile Agent connected to Band. Waiting for resume data...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
