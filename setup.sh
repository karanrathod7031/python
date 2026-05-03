#!/bin/bash
# Jarvis AI Assistant — Setup Script
set -e

echo "======================================"
echo "  Jarvis AI Assistant — Setup"
echo "======================================"

# Check Python version
python3 --version || { echo "Python 3.10+ required"; exit 1; }

# Create virtual environment
echo "[1/6] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "[2/6] Installing backend dependencies..."
pip install --upgrade pip
pip install -e "backend/[dev]"

# Create directories
echo "[3/6] Creating data directories..."
mkdir -p data logs screenshots

# Copy environment file
echo "[4/6] Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env from .env.example — edit as needed."
fi

# Frontend setup (optional)
echo "[5/6] Setting up frontend..."
if command -v node &> /dev/null; then
    cd frontend
    npm install
    cd ..
    echo "  Frontend dependencies installed."
else
    echo "  Node.js not found — skipping frontend setup."
    echo "  Install Node.js 18+ for the dashboard."
fi

# Check Redis (optional)
echo "[6/6] Checking optional services..."
if command -v redis-cli &> /dev/null; then
    redis-cli ping > /dev/null 2>&1 && echo "  Redis: running" || echo "  Redis: not running (optional)"
else
    echo "  Redis: not installed (using in-memory cache fallback)"
fi

if command -v ollama &> /dev/null; then
    echo "  Ollama: installed"
    echo "  Run 'ollama pull llama3' to download the default model."
else
    echo "  Ollama: not installed"
    echo "  Install from https://ollama.ai for AI capabilities."
fi

echo ""
echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo ""
echo "Quick Start:"
echo "  1. Activate: source venv/bin/activate"
echo "  2. Backend:  cd backend && uvicorn app.main:app --reload"
echo "  3. CLI:      cd backend && python cli.py"
echo "  4. Frontend: cd frontend && npm run dev"
echo "  5. Docker:   docker-compose up --build"
echo ""
echo "API docs: http://localhost:8000/docs"
echo "Dashboard: http://localhost:3000"
