# 🌐 LangGraph MCP Server

An MCP server that provides tools for interacting with LangGraph assistants through the [Model Context Protocol](https://modelcontextprotocol.io/introduction).

For detailed information about developing MCP servers:

- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Server Development Quickstart Guide](https://modelcontextprotocol.io/quickstart/server)
- [LangGraph Python SDK](https://langchain-ai.github.io/langgraph/concepts/sdk/) - Essential resource for understanding how to interact with LangGraph clients for your assistants
- [LangGraph Python SDK Reference](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/python_sdk_ref/) - Comprehensive API documentation for client interactions
- [LangGraph Academy Intro to LangGraph](https://academy.langchain.com/courses/intro-to-langgraph) - The Academy's Deployment module is particularly useful for understanding how the LangGraph server works under the hood and how to interact with different client options.

## 📋 Prerequisites

- 🐍 Python 3.11 or higher installed (as specified in uv.lock)
- 🚀 [uv](https://github.com/astral-sh/uv) package manager installed
- 🤖 Access to a LangGraph server

## 🛠️ Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd langgraph-mcp
```

2. Set up the development environment:

```bash
# Step 1: Create a new virtual environment
uv venv

# Step 2: Activate the virtual environment
# On Unix/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Step 3: Install the package
uv pip install .
```
This will:
- Create a Python virtual environment
- Activate it for your terminal session
- Install dependencies from pyproject.toml
## 📁 Project Structure

```
src/
├── settings.py    # Environment and configuration management
└── server.py     # MCP server implementation with tools
```

## ⚙️ Configuration

The server runs on port 50827 by default and requires no environment variables. The LangGraph URL is configured through the MCP settings file.

## 🔧 MCP Settings Configuration

Add the LangGraphMCP server configuration to your MCP settings file. The configuration is the same for both apps, just place it in the appropriate location:

- 🤖 Cline VSCode Extension: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- 💻 Claude Desktop App: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "langgraph_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/langgraph-mcp/src",
        "run",
        "server.py"
      ]
    }
  }
}
```

## 🛠️ Available Tools

The server provides the following MCP tools:

### 🔍 Assistant Management

- `get_assistants_list`: Get list of available assistants. Supports filtering by:
  - Metadata for filtering assistants
  - Graph ID for filtering assistants
  - Maximum number of assistants to return (default: 10)
  - Offset for pagination (default: 0)

### 📊 Schema Operations

- `get_assistant_schema`: Get the schema for an assistant. Useful for knowing how to structure the input of running an assistant using run_assistant.
  - Requires assistant ID to retrieve the schema for

### 🤖 Assistant Execution

- `run_assistant`: Run an assistant with streaming output. Accepts:
  - Assistant ID to run
  - Input data for the assistant
  - Optional thread ID for the assistant run
  - Modes for streaming output (default: ["values"])
  - Optional metadata for the assistant run
  - Optional configuration for the assistant run

### 🔍 Thread Management

- `search_threads`: Search for threads using specified filters:
  - Thread metadata to filter on
  - State values to filter on
  - Thread status filter (allowed: 'idle', 'busy', 'interrupted', 'error')
  - Limit on number of threads to return (default: 10)
  - Offset for pagination (default: 0)

### 📊 Thread State

- `get_state`: Retrieve the state of a thread:
  - Thread ID to get the state for
  - Optional checkpoint information
  - Optional specific checkpoint identifier
  - Option to include subgraphs states (default: false)

## 💻 Local Development

To test the server locally using the MCP CLI:

```bash
mcp dev src/server.py --with-editable .
```

The server will start in development mode with:

- 🔄 Live reloading on file changes
- 🔍 Interactive inspector at http://localhost:5173
- 🐛 Detailed error messages and stack traces

You can test the server's functionality through:

1. 🌐 The MCP Inspector web interface
2. 🤖 Claude with proper MCP settings configuration
3. 📡 Direct HTTP requests to the local server

## 📝 Development Notes

- 🔧 The server uses Pydantic for configuration and request validation
- 🌐 Uses the official LangGraph SDK for API interactions
- 📊 All operations return consistent response formats
