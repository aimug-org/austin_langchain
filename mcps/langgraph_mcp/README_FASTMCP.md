# FastMCP Server Implementation Notes

## Overview
FastMCP provides an ergonomic interface for building Model Context Protocol (MCP) servers, with a focus on simplicity and developer experience. This document outlines key insights about the implementation and usage patterns, particularly when working with stdio transport when the server and client are co-located.

## Key Components

### 1. Server Configuration
- Settings managed via environment variables with `FASTMCP_` prefix
- Configurable options include:
  - Debug mode
  - Log level
  - Host/port (for SSE transport)
  - Resource/tool/prompt warning behaviors

### 2. Core Features

#### Tool Management
- Tools can be registered using `@tool` decorator or `add_tool()` method
- Support for both synchronous and asynchronous functions
- Optional Context injection for accessing MCP capabilities
- Automatic result conversion to appropriate content types

#### Resource Management
- Static resources with fixed URIs
- Template resources with parameterized URIs
- Support for text, binary, and JSON-serializable content
- Registration via `@resource` decorator or `add_resource()` method

#### Prompt Management
- Prompts registered using `@prompt` decorator or `add_prompt()` method
- Support for argument validation
- Can return messages with text or resource content
- Async-compatible prompt generation

### 3. Context Features
- Progress reporting capabilities
- Built-in logging (debug, info, warning, error)
- Resource access during requests
- Request/client identification

## Using with stdio Transport

When the server and client are in the same location (e.g., `/Users/riccardopirruccio/opt/austin_langchain/mcps/langgraph_mcp`), the stdio transport offers several advantages:

1. **Simple Setup**
```python
server = FastMCP(name="MyServer")
server.run(transport="stdio")  # Default transport
```

2. **Direct Communication**
- No network configuration needed
- Lower latency due to direct pipe communication
- Automatic handling of process lifecycle

3. **Development Benefits**
- Easier debugging since everything runs in same process
- Direct access to logs and error messages
- No need to manage network ports or addresses

4. **Context Availability**
- Full access to Context features
- Progress reporting works seamlessly
- Resource access is direct and efficient

## Handling Long-Running Operations

When working with external services like LangGraph that may have long-running operations with streaming output, FastMCP provides robust mechanisms for handling these scenarios effectively.

### Why Use stdio Transport for Long-Running Operations

When connecting to services like a LangGraph server running in a Docker container on the same machine, stdio transport is the optimal choice because:
- Provides direct process communication without network overhead
- Maintains a persistent connection that won't time out
- Handles streaming data naturally through the pipe mechanism
- More reliable for long-running operations compared to HTTP/SSE

### Implementation Patterns

1. **Async Tool with Progress Reporting**
```python
@server.tool(description="Long-running LangGraph operation")
async def langgraph_operation(params: dict, ctx: Context) -> str:
    # 1. Progress Reporting
    await ctx.report_progress(0, 100)
    
    # 2. Status Updates via Logging
    ctx.info("Initializing LangGraph operation...")
    
    # 3. Stream Processing
    async for chunk in langgraph_client.stream_operation(params):
        # Update progress
        await ctx.report_progress(chunk.progress, 100)
        
        # Log intermediate results
        ctx.info(f"Received chunk: {chunk.partial_result}")
        
    return "Operation completed"
```

2. **Best Practices for Long-Running Tools**
- Use async functions to prevent blocking
- Implement proper progress reporting
- Provide regular status updates through logging
- Consider implementing cancellation handling
- Use structured error handling for timeouts/failures

## General Best Practices

1. **Tool Implementation**
```python
@server.tool(description="Example tool")
async def my_tool(param: str, ctx: Context) -> str:
    ctx.info(f"Processing {param}")
    await ctx.report_progress(50, 100)
    return f"Processed {param}"
```

### Parameter Descriptions in Tools
- Use `Annotated` with Pydantic's `Field` to define parameter descriptions in the function signature:
  ```python
  from typing import Annotated
  from pydantic import Field

  @server.tool(description="Example tool")
  async def example_tool(
      param1: Annotated[int, Field(description="An integer parameter")],
      param2: Annotated[str, Field(description="A string parameter")],
  ) -> None:
      pass
  ```

- Ensure that all non-default arguments come before any default arguments in the function signature:
  ```python
  async def example_tool(
      param1: Annotated[int, Field(description="Required parameter")],
      param2: Annotated[Optional[str], Field(description="Optional parameter")] = None,
  ) -> None:
      pass
  ```

These practices ensure that FastMCP's `func_metadata` extracts and exposes parameter descriptions correctly.

2. **Resource Definition**
```python
@server.resource("resource://data/{id}")
async def get_data(id: str) -> dict:
    return {"id": id, "data": "example"}
```

3. **Error Handling**
- Use Context logging for client feedback
- Raise appropriate exceptions for error cases
- Leverage progress reporting for long-running operations

## Design Patterns Used

1. **Decorator Pattern**
- Clean registration of tools, resources, and prompts
- Maintains separation of concerns
- Reduces boilerplate code

2. **Manager Classes**
- Organized functionality by type
- Clear responsibility boundaries
- Simplified maintenance

3. **Context Injection**
- Request-scoped capabilities
- Clean access to MCP features
- Dependency injection pattern

4. **Type Conversion System**
- Flexible content type handling
- Automatic conversions where possible
- Extensible for custom types

## Conclusion

FastMCP provides a robust foundation for building MCP servers with a focus on developer experience. When using stdio transport in a co-located setup, it offers simplified development and debugging while maintaining all the powerful features of the MCP protocol.
