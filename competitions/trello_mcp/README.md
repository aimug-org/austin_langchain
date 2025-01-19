# Trello MCP Server

An MCP server that provides tools for interacting with Trello boards and cards through the Model Context Protocol.

## Prerequisites

- Python 3.8 or higher installed
- pip (Python package manager)
- A Trello account
- Trello API key and token

## Configuration

### Getting Trello Credentials

1. Log in to your Trello account
2. Visit https://trello.com/app-key to get your API key
3. Generate a token by clicking "Generate a Token" on the same page

### Environment Variables

The following environment variables are required in your MCP settings configuration:

```
TRELLO_API_KEY=your_api_key
TRELLO_TOKEN=your_token
```

## MCP Settings Configuration

Add the server configuration to your MCP settings file. The location depends on your setup:

### For Cline VSCode Extension

Location: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "trello": {
      "command": "python",
      "args": ["/path/to/trello-mcp/src/main.py"],
      "env": {
        "TRELLO_API_KEY": "your_api_key",
        "TRELLO_TOKEN": "your_token"
      }
    }
  }
}
```

### For Claude Desktop App

Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "trello": {
      "command": "python",
      "args": ["/path/to/trello-mcp/src/main.py"],
      "env": {
        "TRELLO_API_KEY": "your_api_key",
        "TRELLO_TOKEN": "your_token"
      }
    }
  }
}
```

## Usage Notes

- The server requires Python dependencies to be installed. Use `pip install -r requirements.txt` to install them.
- Ensure the path in the MCP settings configuration points to the main Python script.
- The server will automatically connect when the MCP settings are loaded.
- All API calls are made using the configured credentials.
- Rate limits and quotas from the Trello API apply.

## Available Tools

Once connected, the following MCP tools become available:

- `create_board`: Create a new Trello board
- `create_list`: Create a new list in a board
- `create_card`: Create a new card in a list
- `move_card`: Move a card between lists
- `update_card`: Update card details
- `archive_card`: Archive a card

For detailed tool documentation and schemas, refer to the tool descriptions in your AI assistant's capabilities.
