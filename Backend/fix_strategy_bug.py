#!/usr/bin/env python3
"""
Quick fix for the strategy development bug
"""

# Read the file
with open('app/agents/simple_workflow.py', 'r') as f:
    content = f.read()

# Fix the bug
old_line = 'analysis_summary = str(analysis).get("raw_analysis", str(analysis))[:1000]'
new_line = 'analysis_summary = analysis.get("raw_analysis", str(analysis))[:1000] if isinstance(analysis, dict) else str(analysis)[:1000]'

content = content.replace(old_line, new_line)

# Write back
with open('app/agents/simple_workflow.py', 'w') as f:
    f.write(content)

print("✅ Fixed strategy development bug!") 