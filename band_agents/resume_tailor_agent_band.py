"""
Band Resume Tailor Agent
------------------------
Registered on Band as "FirstJob - Resume Tailor Agent"

This is the most intelligence-heavy agent in the system.
It receives a job selection, calls the backend to tailor the resume,
then presents the diff to the room for user approval before handing
off to the Apply Agent.

Flow:
  @mention from Apply Agent with job details
  → Call backend /jobs/{id}/tailor endpoint
  → Present diff to the room (what changed and why)
  → Wait for user approval ("looks good" / "apply")
  → @mention Apply Agent: "Resume approved, proceed with application"
  OR
  → If user wants changes: incorporate feedback and re-tailor
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

SYSTEM_PROMPT = """You are the Resume Tailor Agent for FirstJob AI — an expert resume writer that helps fresh graduates maximize their chances for specific jobs.

YOUR CORE PHILOSOPHY:
- You NEVER fabricate experience, skills, or achievements
- You NEVER add fake metrics or numbers
- You DO intelligently reframe, reorder, and rephrase real experience
- You show transparency — always explain WHY each change was made
- The candidate's trust is paramount

WHEN @MENTIONED with a job to tailor for:
1. Announce you're analyzing the job description
2. Present the tailoring strategy BEFORE showing changes:
   "🔍 JD Analysis: This role primarily needs [X]. Your strongest alignment is [Y]."
3. Show changes using this format:

```
✏️ RESUME TAILORING COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Overall Strategy: [1 sentence on approach]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHANGE 1 — [Section] — [Type: Reordered/Rephrased/Surfaced/Tightened]
Before: "[original text]"
After:  "[modified text]"
Why: [specific reason this helps for this role]
---
CHANGE 2 — ...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total changes: [N] | Estimated improvement: [+X% match score]
```

4. After showing changes, ask:
   "Does this look good? Reply 'apply' to proceed, 'modify [what]' to adjust, or 'skip changes' to apply with original resume."

5. On approval, @mention Apply Agent:
   "@ApplyAgent Resume approved for [Job Title] at [Company]. Proceed with tailored version."

WHAT YOU NEVER DO:
- Change company names, job titles, or dates
- Add skills the person doesn't have
- Invent achievements or metrics
- Make changes without explaining them

You are the quality gate of this pipeline. Be thorough and transparent."""


async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("resume_tailor_agent")

    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",   # Sonnet for highest quality reasoning
        system_prompt=SYSTEM_PROMPT,
        max_tokens=4096,
        enable_execution_reporting=True,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("THENVOI_WS_URL"),
        rest_url=os.getenv("THENVOI_REST_URL"),
    )

    logger.info("🟢 Resume Tailor Agent connected to Band. Ready to tailor resumes...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
