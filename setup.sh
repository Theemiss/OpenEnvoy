#!/bin/bash

# AI Job Automation System - Setup Script
echo "🚀 Setting up AI Job Automation System"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
if (( $(echo "$python_version < 3.10" | bc -l) )); then
    echo "❌ Python 3.10+ required"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Setup environment
echo "🔧 Configuring environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file - please edit with your configuration"
else
    echo "✅ .env file already exists"
fi

# Setup Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 5

# Initialize database
echo "🗄️ Initializing database..."
python scripts/init_db.py create

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Seed sample data
echo "🌱 Seeding sample data..."
python scripts/seed_data.py

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start the backend: uvicorn backend.main:app --reload"
echo "3. Start the frontend: cd frontend && npm run dev"
echo "4. Run tests: pytest"
echo ""
echo "Access the application:"
echo "- API: http://localhost:8000"
echo "- Dashboard: http://localhost:3000"
echo "- Temporal UI: http://localhost:8233 (if using Temporal)"