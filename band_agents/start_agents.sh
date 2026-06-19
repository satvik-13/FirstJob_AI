#!/bin/bash
# Start all 6 FirstJob Band agents in parallel
# Each runs in the background, logs to its own file

echo "🚀 Starting all FirstJob Band agents..."
echo ""
echo "Prerequisites:"
echo "  1. band-sdk[anthropic] installed: pip install 'band-sdk[anthropic]'"
echo "  2. .env file configured with THENVOI_REST_URL, THENVOI_WS_URL, ANTHROPIC_API_KEY"
echo "  3. agent_config.yaml filled with your Band agent UUIDs and API keys"
echo ""

# Check .env exists
if [ ! -f .env ]; then
  echo "❌ .env not found. Copy the template and fill it in."
  exit 1
fi

# Check agent_config.yaml has been filled
if grep -q "<profile-agent-uuid>" agent_config.yaml; then
  echo "❌ agent_config.yaml still has placeholder UUIDs."
  echo "   Create 6 agents on app.band.ai and fill in their UUIDs and API keys."
  exit 1
fi

mkdir -p logs

echo "Starting Profile Agent..."
python profile_agent_band.py > logs/profile_agent.log 2>&1 &
echo "  PID: $!"

echo "Starting Job Scraper Agent..."
python job_scraper_agent_band.py > logs/job_scraper.log 2>&1 &
echo "  PID: $!"

echo "Starting Resume Tailor Agent..."
python resume_tailor_agent_band.py > logs/resume_tailor.log 2>&1 &
echo "  PID: $!"

echo "Starting Apply Agent..."
python apply_agent_band.py > logs/apply.log 2>&1 &
echo "  PID: $!"

echo "Starting Outreach Agent..."
python outreach_agent_band.py > logs/outreach.log 2>&1 &
echo "  PID: $!"

echo "Starting Tracker Agent..."
python tracker_agent_band.py > logs/tracker.log 2>&1 &
echo "  PID: $!"

echo ""
echo "✅ All 6 agents running!"
echo ""
echo "📋 Next steps:"
echo "  1. Go to app.band.ai"
echo "  2. Create a room called 'FirstJob Workflow'"
echo "  3. Add all 6 agents as participants"
echo "  4. Start a session by typing: '@ProfileAgent New candidate ready'"
echo ""
echo "📄 Logs: tail -f logs/*.log"
echo "🛑 Stop all: kill \$(cat logs/*.pid 2>/dev/null) or pkill -f agent_band"
