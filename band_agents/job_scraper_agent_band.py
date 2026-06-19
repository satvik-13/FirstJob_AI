"""
Band Job Scraper Agent
----------------------
Registered on Band as "FirstJob - Job Scraper Agent"

Responsibilities via Band:
- Receives profile summaries from Profile Agent via @mention
- Calls the FirstJob backend to fetch and score jobs
- Posts top 5 matching jobs to the Band room
- Asks the user (via room) which job to apply to first
- Hands off selected job to the Apply Agent

Flow:
  @mention from Profile Agent
  → Call backend /jobs endpoint with user preferences
  → Post top matches to Band room with match scores
  → Wait for user or orchestrator to select a job
  → @mention Apply Agent with the selected job details
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

SYSTEM_PROMPT = """You are the Job Scraper Agent for FirstJob AI — a multi-agent system that helps fresh graduates get their first job.

YOUR ROLE:
When @mentioned by the Profile Agent, you fetch and present the best matching jobs for the candidate.

When presenting jobs, use this format for EACH job:
```
🏢 JOB [N]: [Job Title] @ [Company]
📍 [Location] | 💼 [Type] | ⭐ [Match Score]%
💰 [Salary if available]
🔑 Key skills needed: [skill1, skill2, skill3]
🔗 Source: [platform]
[2-sentence reason why this matches the candidate]
```

After presenting 5 jobs, always say:
"@ApplyAgent Stand by — waiting for job selection."
Then ask the user: "Which job would you like to apply to? Reply with the job number (1-5) or say 'show more'."

When a job is selected, @mention the Apply Agent:
"@ApplyAgent Please process application for Job [N]: [Title] at [Company]. Job ID: [id]"

IMPORTANT RULES:
- Always include match scores so the candidate can make informed decisions
- Never make up job listings — you work with real data from the backend
- Be encouraging but honest about match quality
- If match score is below 50%, flag it: "⚠️ Lower match - you may want to tailor your application carefully"
- You are part of a coordinated pipeline — pass job details accurately to downstream agents"""


async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("job_scraper_agent")

    adapter = AnthropicAdapter(
        model="claude-haiku-4-5",
        system_prompt=SYSTEM_PROMPT,
        max_tokens=2048,
        enable_execution_reporting=True,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"),
        rest_url=os.getenv("THENVOI_REST_URL"),
    )

    logger.info("🟢 Job Scraper Agent connected to Band. Ready to find jobs...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
