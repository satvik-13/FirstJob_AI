#!/bin/bash
# FirstJob Backend Startup Script

echo "🚀 Starting FirstJob Backend..."

# Check if .env exists
if [ ! -f .env ]; then
  echo "❌ .env file not found. Copy .env.example to .env and fill in your keys."
  exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

echo "✅ Starting FastAPI server on http://localhost:8000"
echo "📖 API docs at http://localhost:8000/docs"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
