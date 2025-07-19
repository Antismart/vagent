#!/usr/bin/env python3
"""
Startup script for the AI Agent Marketplace backend
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the main application
if __name__ == "__main__":
    try:
        from main import app
        import uvicorn
        
        print("🚀 Starting AI Agent Marketplace Backend")
        print("=" * 50)
        print("📡 API will be available at: http://localhost:8000")
        print("📚 API documentation: http://localhost:8000/docs")
        print("🔄 WebSocket endpoint: ws://localhost:8000/ws/{agent_id}")
        print("=" * 50)
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info",
            reload=True  # Enable auto-reload for development
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
