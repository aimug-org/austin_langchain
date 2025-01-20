# 🎯 Trello MCP Server

An MCP server that provides tools for interacting with Trello boards and cards through the [Model Context Protocol](https://modelcontextprotocol.io/introduction).

For detailed information about developing MCP servers:

- [Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Server Development Quickstart Guide](https://modelcontextprotocol.io/quickstart/server)

## 📋 Prerequisites

- 🐍 Python 3.11 or higher installed (as specified in uv.lock)
- 🚀 [uv](https://github.com/astral-sh/uv) package manager installed
- 📊 A Trello account
- 🔑 Trello API key and token

## 🛠️ Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd trello-mcp
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
├── settings.py         # Environment and configuration management
├── trello_client.py    # Trello API client with error handling
├── trello_errors.py    # Custom error handling and exceptions
├── trello_schemas.py   # Pydantic models for request validation
└── server.py          # MCP server implementation with tools
```

## ⚙️ Configuration

### 🔐 Getting Trello Credentials

1. 🔑 Log in to your Trello account
2. 🌐 Visit https://trello.com/app-key to get your API key
3. 🎟️ Generate a token by clicking "Generate a Token" on the same page

### 🌍 Environment Variables

The following environment variables are required:

```
TRELLO_API_KEY=your_api_key
TRELLO_TOKEN=your_token
```

Optional configuration:

```
TRELLO_API_BASE_URL=https://api.trello.com/1  # Default API endpoint
```

## 🔧 MCP Settings Configuration

Add the TrelloMCP server configuration to your MCP settings file. The configuration is the same for both apps, just place it in the appropriate location:

- 🤖 Cline VSCode Extension: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- 💻 Claude Desktop App: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "TrelloMCP": {
      "command": "uv", // Assumes uv is in PATH
      "args": [
        "--directory",
        "/path/to/trello-mcp/src", // Replace with your project's src directory
        "run",
        "server.py"
      ],
      "env": {
        "TRELLO_API_KEY": "your_api_key",
        "TRELLO_TOKEN": "your_token",
        "TRELLO_BOARD_ID": "" // Optional: Set to focus on a specific board
      }
    }
  }
}
```

## 🛠️ Available Tools

The server provides the following MCP tools:

### 📋 Board Operations

- 📊 `list_boards`: Get all boards for the authenticated user
- ➕ `create_board`: Create a new board
- 📑 `get_board_lists`: Get all lists from a specific board
- 📂 `get_board_lists_with_cards`: Get all lists and their cards from a board

### 📝 List Operations

- ➕ `create_list`: Create a new list in a board
- ➕ `create_list_in_default_board`: Create a list in the default board
- 📑 `get_default_board_lists`: Get all lists from the default board
- 📂 `get_list_cards`: Get all cards in a specific list

### 🗂️ Card Operations

- ➕ `create_card`: Create a new card in a list
- 🔄 `move_card`: Move a card between lists
- ✏️ `update_card`: Update card details (name, description, due date)
- 📥 `archive_card`: Archive a card

## ⚠️ Error Handling

The server includes comprehensive error handling:

- 🔒 Authentication errors
- ⏳ Rate limiting
- 🔍 Resource not found
- ✅ Validation errors
- 🚨 Server errors

All API calls include automatic retry logic for transient failures.

## 📝 Development Notes

- 🔧 The server uses Pydantic for configuration and request validation
- 🌐 HTTPX is used for HTTP requests
- 🔄 Automatic retries are implemented for API calls
- 📊 All operations return consistent response formats
- ⚡ Centralized error handling with standardized responses

## 💻 Local Development

To test the server locally using the MCP CLI:

```bash
# With required environment variables
TRELLO_API_KEY="your_api_key" TRELLO_TOKEN="your_token" mcp dev src/server.py --with-editable .

# Or if using environment variables from MCP settings file
mcp dev src/server.py --with-editable .
```

The server will start in development mode with:

- 🔄 Live reloading on file changes
- 🔍 Interactive inspector at http://localhost:5173
- 🐛 Detailed error messages and stack traces

You can test the server's functionality through:

1. 🌐 The MCP Inspector web interface
2. 🤖 Claude with proper MCP settings configuration
3. � Direct HTTP requests to the local server
