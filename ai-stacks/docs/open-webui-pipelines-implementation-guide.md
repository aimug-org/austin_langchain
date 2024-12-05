# Open-WebUI Pipelines Implementation Guide

## Table of Contents
- [Overview](#overview)
- [Core Architecture](#core-architecture)
  - [Base Pipeline Class](#base-pipeline-class)
  - [Valves](#valves)
    - [Key Concepts](#key-concepts)
    - [Implementation Approaches](#implementation-approaches)
    - [Configuration Storage](#configuration-storage)
    - [Best Practices](#best-practices)
  - [Pipeline Types](#pipeline-types)
    - [Filter Pipeline](#1-filter-pipeline)
    - [Function Calling Pipeline](#2-function-calling-pipeline)
    - [Provider Pipeline](#3-provider-pipeline)
- [Resource Management](#resource-management)
  - [Initialization and Cleanup](#initialization-and-cleanup)
  - [Adding Dependencies](#adding-dependencies)
- [Best Practices](#best-practices)
  - [Pipeline Organization](#pipeline-organization)
  - [Resource Management](#resource-management-1)
  - [Error Handling](#error-handling)
  - [Configuration](#configuration)
  - [Testing](#testing)
  - [Module-Level Requirements](#module-level-requirements)

## Overview

Open-WebUI Pipelines is a powerful framework for creating modular, customizable workflows that extend OpenAI API functionality. This guide documents the core components, implementation patterns, and best practices based on real-world usage and community discussions.

## Core Architecture

### Base Pipeline Class

Every pipeline module must define its own `Pipeline` class. The class is not imported from anywhere - it's defined directly in each module. This encapsulation allows each pipeline to be self-contained and independently loadable.

For detailed documentation of pipeline lifecycle methods, see [Pipeline Lifecycle Methods](pipeline-lifecycle-methods.md).

```python
class Pipeline:
    def __init__(self):
        # Optional: Set pipeline ID and name
        # Best practice is to let ID be inferred from filename
        self.name = "My Custom Pipeline"

        # Initialize pipeline valves
        self.valves = self.Valves()

        # Initialize any resources needed
        self._initialize_resources()

    async def on_startup(self):
        """Called when the pipeline server starts"""
        print(f"Starting pipeline: {self.name}")
        # Initialize connections, load models, etc.

    async def on_shutdown(self):
        """Called when the pipeline server stops"""
        print(f"Shutting down pipeline: {self.name}")
        # Clean up resources, close connections

    async def on_valves_updated(self):
        """Called when pipeline valves are updated via API"""
        # React to valve configuration changes
        pass
```

### Valves

Valves are the configuration mechanism for pipelines, allowing users to customize pipeline behavior through the OpenWebUI admin interface. They provide a way for users to modify pipeline settings like API keys, model selection, and other parameters.

#### Key Concepts

- Valves allow users to change pipeline behavior without modifying code
- Common use cases include:
  - API keys for external services
  - Model selection and parameters
  - Custom prompts and settings
  - Filter pipeline targeting and priority

#### Implementation Approaches

1. **Direct Assignment**
   The simplest approach, defining valves directly in the class:
   ```python
   class Pipeline:
       class Valves(BaseModel):
           # Basic settings
           enabled: bool = True
           debug_mode: bool = False

           # Optional configurations
           api_key: Optional[str] = None
           model_name: Optional[str] = None

           # Filter settings
           pipelines: List[str] = ["*"]
           priority: int = 0
   ```

2. **Dictionary Unpacking**
   More flexible approach using environment variables:
   ```python
   class Pipeline:
       class Valves(BaseModel):
           api_key: str
           model_name: str = "gpt-3.5-turbo"
           base_url: str = "http://localhost:11434"

       def __init__(self):
           self.valves = self.Valves(
               **{
                   "api_key": os.getenv("PIPELINE_API_KEY", "default-key"),
                   "model_name": os.getenv("PIPELINE_MODEL", "gpt-3.5-turbo"),
                   "base_url": os.getenv("PIPELINE_URL", "http://localhost:11434")
               }
           )
   ```

#### Configuration Storage

- Valves are stored in `valves.json` in the pipeline's directory
- Configurations can be updated through OpenWebUI admin interface
- Changes trigger the `on_valves_updated` method:
  ```python
  async def on_valves_updated(self):
      """React to valve configuration changes"""
      if self.valves.api_key:
          self.client = await self._setup_client(self.valves.api_key)
  ```

#### Best Practices

1. **Use Optional Types for Flexibility**
   ```python
   class Valves(BaseModel):
       api_key: Optional[str] = None
       custom_prompt: Optional[str] = None
   ```

2. **Support Environment Variables**
   ```python
   def __init__(self):
       self.valves = self.Valves(
           **{
               "api_key": os.getenv("PIPELINE_API_KEY"),
               "base_url": os.getenv("PIPELINE_BASE_URL")
           }
       )
   ```

3. **Validate Values**
   ```python
   class Valves(BaseModel):
       temperature: float = Field(
           default=0.7,
           ge=0.0,
           le=1.0,
           description="Controls randomness"
       )
   ```

4. **Document Purpose**
   ```python
   class Valves(BaseModel):
       """Pipeline configuration valves

       Attributes:
           api_key: API key for external service
           model_name: Name of the model to use
       """
   ```

### Pipeline Types

#### 1. Filter Pipeline

Filter pipelines intercept messages before they reach the LLM and after the LLM responds. Use cases include:
- RAG for context injection
- Safety filters
- Tool execution
- Prompt modification

```python
class Pipeline:
    def __init__(self):
        self.type = "filter"
        self.valves = self.Valves()

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """Modify messages before LLM"""
        messages = body.get("messages", [])
        user_message = get_last_user_message(messages)

        if user_message:
            # Add context, modify prompt
            context = await self._get_context(user_message)
            user_message["content"] = f"{context}\n\n{user_message['content']}"

        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """Modify messages after LLM"""
        messages = body.get("messages", [])
        assistant_message = get_last_assistant_message(messages)

        if assistant_message:
            # Post-process response
            processed = await self._process_response(assistant_message["content"])
            assistant_message["content"] = processed

        return body
```

#### 2. Function Calling Pipeline

Implements tool selection and execution:

```python
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint

class Pipeline(FunctionCallingBlueprint):
    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def calculator(self, equation: str) -> str:
            """Calculate mathematical expressions"""
            try:
                result = eval(equation)
                return f"{equation} = {result}"
            except Exception as e:
                return f"Error: {str(e)}"

    def __init__(self):
        super().__init__()
        self.name = "Calculator Pipeline"
        self.tools = self.Tools(self)
```

Notes:
- Inherit from FunctionCallingBlueprint
- Define tools in Tools class
- Use `__` prefix to hide helper functions
- Access valves via `self.pipeline.valves`
- TASK_MODEL valve controls tool selection

#### 3. Provider Pipeline

Implements custom LLM providers or complex workflows:

```python
class Pipeline:
    def __init__(self):
        self.type = "pipe"  # or "manifold" for multi-model
        self.valves = self.Valves()

    def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[dict],
        body: dict
    ) -> Union[str, Generator, Iterator]:
        """Process messages and return response"""
        formatted = self._format_messages(messages)
        response = self.client.generate(formatted)
        return response.text
```

For multiple models, use manifold type:

```python
class Pipeline:
    def __init__(self):
        self.type = "manifold"

    def pipelines(self) -> List[dict]:
        """Available models"""
        return [
            {"id": "gpt-4", "name": "GPT-4"},
            {"id": "gpt-3.5", "name": "GPT-3.5"}
        ]

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict):
        # Use model_id to select specific model
        response = self.client.generate(messages, model=model_id)
        return response
```

## Resource Management

### Initialization and Cleanup

```python
class Pipeline:
    def __init__(self):
        self.resources = {}
        self._initialize_resources()

    def _initialize_resources(self):
        """Initialize pipeline resources"""
        # Setup vector store
        self.resources["vector_store"] = self._setup_vector_store()

        # Initialize embeddings
        self.resources["embeddings"] = self._setup_embeddings()

        # Setup API client
        self.resources["client"] = self._setup_client()

    async def on_startup(self):
        """Initialize async resources"""
        self.resources["session"] = aiohttp.ClientSession()

    async def on_shutdown(self):
        """Clean up resources"""
        # Close connections
        if "session" in self.resources:
            await self.resources["session"].close()

        # Clean up other resources
        for resource in self.resources.values():
            if hasattr(resource, "close"):
                await resource.close()
```

### Adding Dependencies

Use front-matter to specify pip requirements:

```python
"""
title: Custom Pipeline
author: Your Name
version: 1.0
license: MIT
description: Pipeline description
requirements: requests,beautifulsoup4,numpy
"""

class Pipeline:
    # Pipeline implementation
```

The requirements will be installed when the pipeline is loaded via `PIPELINES_URLS` environment variable:

```bash
docker run -d -p 9099:9099 \
  --add-host=host.docker.internal:host-gateway \
  -e PIPELINES_URLS="https://raw.githubusercontent.com/user/repo/main/custom_pipeline.py" \
  -v pipelines:/app/pipelines \
  --name pipelines \
  --restart always \
  ghcr.io/open-webui/pipelines:main
```

## Best Practices

1. **Pipeline Organization**
   - One pipeline per file
   - Clear, descriptive pipeline names
   - Group related pipelines in subdirectories
   - Use valves.json for configuration

2. **Resource Management**
   - Initialize resources in on_startup
   - Clean up in on_shutdown
   - Use context managers where possible
   - Handle errors gracefully

3. **Error Handling**
   - Validate inputs
   - Catch and log exceptions
   - Return meaningful error messages
   - Clean up resources on failure

4. **Configuration**
   - Use Valves for user configuration
   - Validate configuration values
   - Provide sensible defaults
   - Document configuration options

5. **Testing**
   - Write unit tests for components
   - Test error handling
   - Verify resource cleanup
   - Test with different configurations
6. **Module-Level Requirements**
   - Add encoding declaration at the top of the file:
     ```python
     # -*- coding: utf-8 -*-
     ```
   - Explicitly expose the Pipeline class at the module level:
     ```python
     __all__ = ["Pipeline"]
     ```
   - This ensures the pipeline server can properly discover and load the Pipeline class
   - Without proper module-level exposure, you may encounter "No Pipeline class found" errors
Remember:
- Pipeline class is defined in each module
- Use lifecycle methods appropriately
- Handle resources properly
- Document configuration options
- Test thoroughly before deployment
