#!/usr/bin/env python3
"""
Campaign AI Unified Startup Script

This script starts both the FastAPI application and MCP server together,
providing a complete Campaign AI system with:
- Direct REST API endpoints for data display (campaigns, analytics)
- MCP-integrated endpoints for agentic operations (optimization, analysis)
- Automatic MCP server management
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

def print_banner():
    """Print startup banner."""
    print("=" * 60)
    print("🚀 Campaign AI - Unified System Startup")
    print("=" * 60)
    print("📊 FastAPI Server: Direct data access for frontend")
    print("🤖 MCP Server: Agentic operations and tool access")
    print("🔗 Integration: Seamless frontend-backend connection")
    print("=" * 60)

def main():
    """Start the unified Campaign AI system."""
    print_banner()
    
    # Get configuration from environment
    port = os.getenv("PORT", "8000")
    host = os.getenv("HOST", "0.0.0.0")
    
    # Get paths
    backend_dir = Path(__file__).parent
    fastapi_main = backend_dir / "app" / "main.py"
    
    if not fastapi_main.exists():
        print(f"❌ FastAPI main.py not found at: {fastapi_main}")
        sys.exit(1)
    
    print(f"📍 Backend directory: {backend_dir}")
    print(f"📍 FastAPI main: {fastapi_main}")
    print()
    
    # Start the FastAPI application (which will auto-start MCP server)
    print("🚀 Starting Campaign AI FastAPI Application...")
    print(f"   - FastAPI server will start on http://{host}:{port}")
    print("   - MCP server will be started automatically")
    print("   - All endpoints will be available")
    print()
    print("📋 Available endpoints:")
    print("   📊 Data Access:")
    print("      GET  /api/campaigns - List campaigns")
    print("      GET  /api/dashboard/stats - Dashboard statistics")
    print("      GET  /api/campaigns/{id} - Campaign details")
    print("   🤖 Agentic Operations:")
    print("      POST /optimize - Campaign optimization")
    print("      POST /workflow - Full workflow execution")
    print("      POST /api/mcp - Direct MCP tool calls")
    print("   🔧 System:")
    print("      GET  /health - Health check")
    print("      GET  /tools - Available MCP tools")
    print()
    print("⏹️  Press Ctrl+C to stop all services")
    print("-" * 60)
    
    try:
        # Run FastAPI with uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app",
            "--host", host,
            "--port", port,
            "--reload"
        ], cwd=backend_dir, check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  Campaign AI system stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Campaign AI system failed with exit code: {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main() 