#!/bin/bash

# AI-Powered Task Manager API Setup Script
# This script helps set up the development environment

set -e

echo "🚀 Setting up AI-Powered Task Manager API..."

# Check Python version
echo "📦 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python 3.10+ is required. Found: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Setup environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Don't forget to add your ANTHROPIC_API_KEY to .env"
else
    echo "⚠️  .env file already exists"
fi

# Check PostgreSQL
echo "🐘 Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL is installed"
    
    # Check if database exists
    if psql -lqt | cut -d \| -f 1 | grep -qw taskmanager; then
        echo "✅ Database 'taskmanager' exists"
    else
        echo "📊 Creating database 'taskmanager'..."
        createdb taskmanager || echo "⚠️  Could not create database. You may need to do this manually."
    fi
else
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL:"
    echo "   - macOS: brew install postgresql"
    echo "   - Ubuntu: sudo apt-get install postgresql"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the application: uvicorn main:app --reload"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "Or use Docker:"
echo "1. docker-compose up --build"
echo ""
