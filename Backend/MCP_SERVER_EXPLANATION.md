# MCP Server Architecture & Client Connection Guide

## 🖥️ **How the MCP Server Actually Works**

### **Automatic Server Startup (Current Implementation)**

Your agents **automatically start the MCP server** when they need it:

```python
# This code in your agents automatically starts the server
server_params = StdioServerParameters(
    command="python3",
    args=["/path/to/campaign_ai_server.py"],
)

async with stdio_client(server_params) as (read, write):
    # This line STARTS the server as a subprocess!
    async with ClientSession(read, write) as session:
        # Now connected to the running server
```

**What happens behind the scenes:**
1. `stdio_client` spawns `python3 campaign_ai_server.py` as a subprocess
2. Client communicates with server via stdin/stdout pipes
3. When the context exits, the server process is automatically terminated

### **Manual Server Startup (For UI/Frontend)**

For your UI to connect, you have two options:

#### **Option 1: Use the Automatic Pattern (Recommended)**
Your frontend can use the same pattern as the agents:

```javascript
// In your frontend (if using Node.js MCP client)
const serverParams = {
    command: "python3",
    args: ["/path/to/campaign_ai_server.py"]
};

// The MCP client library will start the server automatically
```

#### **Option 2: Manual Server Management**
Use the `start_mcp_server.py` script I created:

```bash
# Start the server manually
python3 start_mcp_server.py

# Output:
# ✅ MCP Server running:
#    📍 Path: /path/to/campaign_ai_server.py
#    🆔 PID: 12345
#    📡 Command: python3 /path/to/campaign_ai_server.py
```

## 🔌 **Client Connection Architecture**

### **Current Client Types:**

1. **Agent Clients** (campaign_agent.py, coordinator.py, etc.)
   - Auto-start server per session
   - Use `stdio_client` with `StdioServerParameters`
   - Temporary connections for workflow execution

2. **Standalone Client** (campaign_ai_client.py)
   - Can connect to existing server or auto-start
   - Used for testing and direct tool access

3. **Your Future UI Client**
   - Should use the same auto-start pattern
   - Or connect to a manually started server

### **Connection Flow:**

```
Frontend/UI
    ↓
MCP Client Library
    ↓
StdioServerParameters(command="python3", args=["campaign_ai_server.py"])
    ↓
Subprocess: python3 campaign_ai_server.py
    ↓
14 Tools Available: analyze_campaign_performance, get_facebook_campaigns, etc.
```

## 🛠️ **Tool Access Pattern**

### **How Tools Are Exposed:**

1. **Server Side** (`campaign_ai_server.py`):
   ```python
   @server.list_tools()
   async def handle_list_tools() -> list[types.Tool]:
       return [
           types.Tool(name="analyze_campaign_performance", ...),
           types.Tool(name="get_facebook_campaigns", ...),
           # ... 14 total tools
       ]
   ```

2. **Client Side** (Any client):
   ```python
   # List available tools
   tools = await client.list_tools()
   
   # Call a specific tool
   result = await client.call_tool("analyze_campaign_performance", {
       "campaign_data": "...",
       "time_period": "last_7_days"
   })
   ```

## 🎯 **For Your UI Implementation**

### **Recommended Approach:**

1. **Use MCP Client Library** in your frontend framework
2. **Auto-start the server** using the same pattern as agents
3. **Connect once** and reuse the connection
4. **Call tools directly** without going through agents

### **Example Frontend Connection:**

```typescript
// Example for a React/Node.js frontend
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

class CampaignAIClient {
    private client: Client;
    
    async connect() {
        const transport = new StdioClientTransport({
            command: 'python3',
            args: ['/path/to/campaign_ai_server.py']
        });
        
        this.client = new Client({
            name: "campaign-ai-ui",
            version: "1.0.0"
        }, {
            capabilities: {}
        });
        
        await this.client.connect(transport);
    }
    
    async analyzeCampaigns(campaignData: string) {
        return await this.client.callTool({
            name: "analyze_campaign_performance",
            arguments: {
                campaign_data: campaignData,
                time_period: "last_7_days"
            }
        });
    }
}
```

## 🚀 **Testing Your Setup**

### **1. Test Manual Server Startup:**
```bash
cd Backend
python3 start_mcp_server.py
```

### **2. Test Agent Connection:**
```bash
cd Backend  
python3 comprehensive_system_test.py
```

### **3. Test Direct Tool Access:**
```python
from app.mcp.client.campaign_ai_client import CampaignAIClient

async def test():
    client = CampaignAIClient()
    await client.connect()
    tools = await client.list_tools()
    print(f"Available tools: {[t.name for t in tools.tools]}")
```

## 📋 **Summary**

### **Key Points:**
1. **Server Auto-Starts**: Clients automatically start the server when connecting
2. **No Manual Management Needed**: The stdio pattern handles server lifecycle
3. **Multiple Clients Supported**: Each client gets its own server instance
4. **14 Tools Available**: All accessible via MCP protocol
5. **UI Can Connect Directly**: No need to go through agents

### **Your UI Architecture Should Be:**
```
UI Frontend → MCP Client → Auto-Started Server → 14 Tools
```

**Not:**
```
UI Frontend → Agent → MCP Client → Server → Tools
```

This gives you direct access to all tools while maintaining the MCP protocol benefits! 