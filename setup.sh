#!/bin/bash

# AI Agent Marketplace Startup Script

echo "🚀 Starting AI Agent Marketplace with vLEI"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
if ! npm install; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
if ! pip install -r requirements.txt; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

cd ..

echo "✅ Installation completed successfully!"
echo ""
echo "🎯 What's next:"
echo "1. Start the application:"
echo "   npm run start:dev"
echo ""
echo "2. Or start components separately:"
echo "   Backend:  cd backend && python main.py"
echo "   Frontend: npm run dev"
echo ""
echo "3. Run the demo script (after starting backend):"
echo "   cd backend && python demo.py"
echo ""
echo "4. Open your browser:"
echo "   Frontend: http://localhost:5173"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo "📚 Read the README.md for detailed usage instructions"
