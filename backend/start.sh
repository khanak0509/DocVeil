#!/bin/bash

echo "🚀 Starting DocVeil Backend Server..."
echo ""

# Check if Ollama is running
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install Ollama first."
    exit 1
fi

# Check if llama3.1:8b model is available
if ! ollama list | grep -q "llama3.1:8b"; then
    echo "⚠️  llama3.1:8b model not found."
    echo "Pulling model... (this may take a while)"
    ollama pull llama3.1:8b
fi

echo "✅ All dependencies ready!"
echo ""
echo "📡 Starting FastAPI server on http://localhost:8000"
echo "📖 API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the server
python api.py
