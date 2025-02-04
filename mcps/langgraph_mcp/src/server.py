"""MCP server implementation for LangGraph using FastMCP.

This implementation defers connection to LangGraph until a tool is called.
All logging intended for the client is performed via the Context’s logging methods
(which send messages over the MCP protocol via stdio) rather than using module-level logging.
"""

from typing import Optional, Annotated
from pydantic import Field
from mcp.server.fastmcp.server import FastMCP, Context
from langgraph_sdk import get_client
from langgraph_sdk.schema import Assistant, GraphSchema, StreamPart, StreamMode, Json, Config
from settings import Settings

# Initialize settings (do not log here to avoid writing to stdout)
settings = Settings()

# Global placeholder for the LangGraph client.
_client = None

def get_langgraph_client(ctx: Context):
    """
    Lazily initialize and return the LangGraph client using the provided context for logging.

    This function uses the Context’s logging methods so that status messages are sent
    via the MCP protocol (over stdio) and not written directly to stdout.
    """
    global _client
    if _client is None:
        try:
            ctx.debug(f"Connecting to LangGraph at {settings.URL}")
            _client = get_client(url=settings.URL)
            ctx.debug("LangGraph client initialized")
        except Exception as e:
            ctx.error(f"Failed to connect to LangGraph server: {e}")
            raise RuntimeError(
                f"LangGraph server not available at {settings.URL}. "
                f"Please ensure the server is running on port {settings.PORT}."
            )
    return _client

# Initialize the FastMCP server.
server = FastMCP(name="langgraph_mcp")

@server.tool(description="Get list of available assistants")
async def get_assistants_list(
    ctx: Context,
    metadata: Annotated[Json, Field(description="Optional metadata for filtering assistants")] = None,
    graph_id: Annotated[Optional[str], Field(description="Optional graph ID for filtering assistants")] = None,
    limit: Annotated[int, Field(description="Maximum number of assistants to return")] = 10,
    offset: Annotated[int, Field(description="Offset for pagination")] = 0,
) -> list[Assistant]:
    """Search for assistants with optional filtering."""
    ctx.debug(f"Searching assistants with limit={limit}, offset={offset}")
    try:
        client = get_langgraph_client(ctx)
        assistants = await client.assistants.search(
            metadata=metadata,
            graph_id=graph_id,
            limit=limit,
            offset=offset,
        )
        ctx.debug(f"Found {len(assistants)} assistants")
        return assistants
    except Exception as e:
        ctx.error(f"Error searching assistants: {e}")
        raise

@server.tool(description="Get the schema for an assistant. Useful for knowing how to structure the input of running an assistant using run_assistant")
async def get_assistant_schema(
    ctx: Context,
    assistant_id: Annotated[str, Field(description="The ID of the assistant to retrieve the schema for")],
) -> GraphSchema:
    """Get the schema for an assistant by ID."""
    ctx.debug(f"Getting schema for assistant {assistant_id}")
    try:
        client = get_langgraph_client(ctx)
        schema = await client.assistants.get_schemas(assistant_id=assistant_id)
        ctx.debug("Successfully retrieved assistant schema")
        return schema
    except Exception as e:
        ctx.error(f"Error getting assistant schema: {e}")
        raise

@server.tool(description="Run an assistant with streaming output")
async def run_assistant(
    ctx: Context,
    assistant_id: Annotated[str, Field(description="The ID of the assistant to run")],
    input: Annotated[dict, Field(description="Input data for the assistant")],
    thread_id: Annotated[Optional[str], Field(description="Optional thread ID for the assistant run")] = None,
    stream_mode: Annotated[list[StreamMode], Field(description="Modes for streaming output")] = ["values"],
    metadata: Annotated[Json, Field(description="Optional metadata for the assistant run")] = None,
    config: Annotated[Optional[Config], Field(description="Optional configuration for the assistant run")] = None,
) -> dict:
    """Run an assistant and stream the results."""
    ctx.debug(f"Starting assistant run for {assistant_id}")
    try:
        client = get_langgraph_client(ctx)
        messages = []
        async for chunk in client.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            input=input,
            stream_mode=stream_mode,
            metadata=metadata,
            config=config,
        ):
            if isinstance(chunk, StreamPart):
                if chunk.event == "metadata":
                    ctx.debug(f"Run metadata: {chunk.data}")
                    await ctx.report_progress(10, 100)
                elif chunk.event == "values":
                    await ctx.report_progress(50, 100)
                    ctx.debug(f"Received values: {chunk.data}")
                    if chunk.data:
                        messages.extend(chunk.data.get("messages", []))
                elif chunk.event == "end":
                    await ctx.report_progress(100, 100)
                    ctx.debug("Run completed")
        return {"messages": messages}
    except Exception as e:
        ctx.error(f"Error during assistant run: {e}")
        raise


@server.tool(description="Search for threads using specified filters")
async def search_threads(
    ctx: Context,
    metadata: Optional[Json] = Field(default=None, description="Thread metadata to filter on"),
    values: Optional[Json] = Field(default=None, description="State values to filter on"),
    status: Optional[str] = Field(default=None, description="Thread status filter; allowed: 'idle', 'busy', 'interrupted', 'error'"),
    limit: int = Field(default=10, description="Limit on number of threads to return"),
    offset: int = Field(default=0, description="Offset for pagination")
) -> list:
    """
    Searches for threads based on metadata, state values, and status.
    """
    client = get_langgraph_client(ctx)
    threads = await client.threads.search(
        metadata=metadata,
        values=values,
        status=status,
        limit=limit,
        offset=offset
    )
    return threads

@server.tool(description="Retrieve the state of a thread")
async def get_state(
    ctx: Context,
    thread_id: str = Field(..., description="The ID of the thread to get the state for"),
    checkpoint: Optional[dict] = Field(default=None, description="Checkpoint information (if applicable)"),
    checkpoint_id: Optional[str] = Field(default=None, description="Specific checkpoint identifier"),
    subgraphs: bool = Field(default=False, description="Include subgraphs states")
) -> dict:
    """
    Retrieves the current state of the specified thread.
    """
    client = get_langgraph_client(ctx)
    state = await client.threads.get_state(
        thread_id=thread_id,
        checkpoint=checkpoint,
        checkpoint_id=checkpoint_id,
        subgraphs=subgraphs
    )
    return state

if __name__ == "__main__":
    # Run the server using stdio transport.
    # With stdio transport, only MCP messages (and client-directed logs via Context)
    # should be written to stdout.
    server.run(transport="stdio")
