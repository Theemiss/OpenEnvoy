#!/bin/bash

# Test Runner Script
echo "🧪 Running AI Job Automation Tests"

# Activate virtual environment
source venv/bin/activate

# Set test environment
export ENVIRONMENT=test
export DATABASE_URL=sqlite+aiosqlite:///:memory:
export REDIS_URL=redis://localhost:6379/1

# Run tests with coverage
echo "📊 Running pytest with coverage..."
pytest tests/ \
    --cov=backend \
    --cov-report=term \
    --cov-report=html:coverage_report \
    --cov-report=xml:coverage.xml \
    -v \
    --tb=short

# Check test status
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    
    # Show coverage summary
    echo ""
    echo "Coverage Summary:"
    coverage report --omit="*/tests/*,*/migrations/*"
    
    # Open coverage report
    if [ "$1" == "--open" ]; then
        open coverage_report/index.html
    fi
else
    echo "❌ Tests failed"
    exit 1
fi

# Run specific test types
if [ "$1" == "--unit" ]; then
    echo "Running unit tests only..."
    pytest tests/unit -v
    
elif [ "$1" == "--integration" ]; then
    echo "Running integration tests only..."
    pytest tests/integration -v
    
elif [ "$1" == "--scraper" ]; then
    echo "Running scraper tests..."
    pytest tests/unit/test_github_ingestion.py tests/integration/test_job_pipeline.py -v
fi