# FirstJob AI 🎯
> Multi-agent AI system that gets fresh graduates their first job — built for lablab.ai Band of Agents Hackathon (June 12–19, 2026)

## What it does

Fresh graduates send hundreds of generic applications and hear nothing back. FirstJob fixes that with 6 coordinated AI agents:

1. **Profile Agent** — parses your resume into a structured profile (the source of truth for everything else)
2. **Job Scraper Agent** — pulls jobs from Indeed, LinkedIn, Naukri, Internshala and scores each against your profile
3. **Resume Tailor Agent** — intelligently rewrites your resume for each job (rephrases, reorders, surfaces buried skills — never fabricates)
4. **Apply Agent** — Tinder-style swipe UI, one tap to apply
5. **Outreach Agent** — automatically finds the HR/hiring manager and sends a personalized cold email from your own Gmail
6. **Tracker Agent** — Kanban dashboard + Excel export of every application with status tracking

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), PostgreSQL |
| AI | Anthropic Claude (claude-sonnet-4-6 for reasoning, claude-haiku-4-5 for parsing) |
| Agent Framework | Band (lablab.ai) |
| Job Data | JSearch API (RapidAPI) — real Indeed/LinkedIn/Glassdoor |
| Email | Gmail API (OAuth2) |
| Contact Finding | Hunter.io |
| Frontend | React 18, Vite, Tailwind CSS, Framer Motion, Zustand |
| Task Queue | Redis + Celery (background outreach) |

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (running locally)
- Redis (running locally)

**API Keys needed (all free tier):**
- Anthropic API key → [console.anthropic.com](https://console.anthropic.com)
- RapidAPI key (JSearch) → [rapidapi.com](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
- Google OAuth credentials → [console.cloud.google.com](https://console.cloud.google.com)
- Hunter.io key (optional) → [hunter.io](https://hunter.io)

---

## Setup & Run

### 1. Clone and configure

```bash
git clone <repo>
cd firstjob
```

### 2. Backend setup

```bash
cd backend

# Copy and fill in environment variables
cp .env.example .env
# Edit .env with your API keys

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Create the database
createdb firstjob               # Mac/Linux with psql installed
# Or create via pgAdmin on Windows
```

### 3. Start backend

```bash
# Make sure PostgreSQL and Redis are running, then:
bash start.sh

# OR manually:
uvicorn main:app --reload --port 8000
```

API will be live at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### 4. Frontend setup

```bash
cd ../frontend
npm install
npm run dev
```

Frontend live at `http://localhost:3000`

---

## First Run Walkthrough

1. Open `http://localhost:3000` → **Create account**
2. Upload your resume (PDF or DOCX) → AI parses it instantly
3. Set your preferences (domain, location, job type)
4. Go to **Jobs** → start swiping
5. Tap **Apply + Tailor Resume** on any card → see what the AI changed
6. Connect Gmail in **Profile** tab → cold emails will auto-send after each application
7. Track everything in **Tracker** → export to Excel anytime

---

## Project Structure

```
firstjob/
├── backend/
│   ├── agents/
│   │   ├── profile_agent.py        # Resume parsing
│   │   ├── job_scraper_agent.py    # Multi-source job fetching + scoring
│   │   ├── resume_tailor_agent.py  # Intelligent resume tailoring (core AI)
│   │   ├── outreach_agent.py       # Cold email finder + writer + sender
│   │   └── tracker_agent.py        # Excel export + stats
│   ├── api/routes/
│   │   ├── auth.py                 # Register, login, JWT
│   │   ├── profile.py              # Resume upload, preferences
│   │   ├── jobs.py                 # Job feed, save, apply
│   │   ├── applications.py         # Tracker CRUD, Excel export
│   │   └── gmail.py                # Gmail OAuth flow
│   ├── core/
│   │   ├── config.py               # Settings from .env
│   │   └── database.py             # Async SQLAlchemy setup
│   ├── models/                     # SQLAlchemy ORM models
│   └── main.py                     # FastAPI app entry point
│
└── frontend/
    └── src/
        ├── pages/
        │   ├── OnboardingPage.jsx  # Resume upload + preferences
        │   ├── JobsPage.jsx        # Swipe UI
        │   ├── TrackerPage.jsx     # Application tracker
        │   ├── OutreachPage.jsx    # Cold email log
        │   └── ProfilePage.jsx     # Profile + Gmail connect
        ├── components/
        │   ├── jobs/JobCard.jsx    # Swipeable job card
        │   ├── jobs/ResumeDiffModal.jsx  # Shows AI resume changes
        │   └── AppLayout.jsx       # Bottom nav layout
        └── store/
            ├── authStore.js        # Zustand auth state
            └── jobsStore.js        # Zustand jobs state
```

---

## Resume Tailor Agent — How it actually works

Most resume tools do keyword stuffing. We don't.

**Step 1 — Deep JD analysis:** Claude reads the full job description and extracts core responsibilities, implied priorities, domain vocabulary, and culture signals — not just a keyword list.

**Step 2 — Profile mapping:** For each JD requirement, the agent finds the closest real match in the user's actual experience. If something genuinely isn't there, it stays absent. No fabrication.

**Step 3 — Intelligent rewriting:**
- Reorders bullet points to lead with most relevant
- Rephrases using the JD's own vocabulary (same meaning, better alignment)
- Surfaces skills buried inside bullet points into the skills section
- Tightens wordy bullets for impact

**Step 4 — Safety check:** Code-level guard that reverts any changes to company names, job titles, dates, or education — these are never touched.

**Step 5 — Diff + approval:** User sees old vs new with reasons for every change before submitting.

---

## Cold Outreach Agent — How it works

After every application:
1. Hunter.io lookup for HR/recruiter at the company
2. Falls back to email pattern guessing if Hunter has no data
3. Claude writes a ≤100 word personalized email — references something specific about the company, mentions 1-2 genuinely relevant things from the user's background
4. Sent via the user's own Gmail (not a third-party sender)
5. Follow-up scheduled for 4 days later if no reply
6. All tracked in the Outreach tab

---

## Hackathon Info

- **Event:** Band of Agents Hackathon — lablab.ai
- **Dates:** June 12–19, 2026
- **Framework:** Band (multi-agent coordination)
- **Team:** Solo

---

## Environment Variables

```env
ANTHROPIC_API_KEY=sk-ant-...
RAPIDAPI_KEY=...
HUNTER_API_KEY=...          # Optional
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/firstjob
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-random-32-char-secret
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```
