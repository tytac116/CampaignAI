#!/usr/bin/env python3
"""
Run Campaign AI MCP Server

Simple script to start the MCP server for testing and UI integration.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the MCP server."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    server_path = script_dir / "mcp_server.py"
    
    if not server_path.exists():
        print(f"❌ MCP server not found at: {server_path}")
        sys.exit(1)
    
    print("🚀 Starting Campaign AI MCP Server...")
    print(f"📍 Server path: {server_path}")
    print("🔗 Server will be available for MCP client connections")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the MCP server
        subprocess.run([sys.executable, str(server_path)], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  MCP server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ MCP server failed with exit code: {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main() 