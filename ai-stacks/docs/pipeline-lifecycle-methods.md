# Pipeline Lifecycle Methods

This document details the lifecycle methods available in the Pipeline class and best practices for their implementation.

## Overview

Pipeline lifecycle methods are special methods that are called at specific points during a pipeline's existence. They help manage resources, handle state changes, and ensure proper cleanup.

## Core Lifecycle Methods

### `__init__`

The constructor is called when a pipeline instance is created.

```python
def __init__(self):
    # Optional: Set pipeline ID, name and type
    self.id = "my-pipeline"  # Used for routing and identification
    self.name = "My Custom Pipeline"
    self.type = "pipe"  # Options: "pipe", "filter", "manifold"

    # Initialize pipeline valves
    self.valves = self.Valves()

    # Initialize any non-async resources
    self._initialize_resources()
```

**Best Practices:**
- Set basic pipeline properties (id, name, type)
- Initialize valve configurations
- Set up non-async resources
- Don't perform async operations (use `on_startup` instead)

### `on_startup`

Called when the pipeline server starts. Use this for async initialization tasks.

```python
async def on_startup(self):
    """Initialize async resources when pipeline server starts"""
    # Initialize connections
    self.session = aiohttp.ClientSession()

    # Load models
    self.model = await self._load_model()

    # Set up databases
    self.db = await self._initialize_database()
```

**Best Practices:**
- Initialize async resources (DB connections, API clients)
- Load models into memory
- Set up network connections
- Log startup progress

### `on_shutdown`

Called when the pipeline server stops or when a pipeline is deleted. Use this for cleanup tasks.

```python
async def on_shutdown(self):
    """Clean up resources when pipeline server stops or pipeline is deleted"""
    # Close network connections
    if hasattr(self, 'session'):
        await self.session.close()

    # Clean up database connections
    if hasattr(self, 'db'):
        await self.db.close()

    # Free model resources
    if hasattr(self, 'model'):
        await self.model.unload()
```

**Best Practices:**
- Close all open connections
- Free memory resources
- Ensure proper cleanup of all initialized resources
- Handle cleanup errors gracefully

### `on_valves_updated`

Called when pipeline valves are updated via the API. The updated valves are automatically persisted to a valves.json file.

```python
async def on_valves_updated(self):
    """React to valve configuration changes"""
    # Reinitialize clients with new settings
    if self.valves.api_key:
        self.client = await self._setup_client(self.valves.api_key)

    # Update model parameters
    if self.valves.model_name:
        await self._update_model_config(self.valves.model_name)
```

**Best Practices:**
- Validate new valve configurations
- Update relevant resources with new settings
- Handle configuration errors gracefully
- Log configuration changes
- Note that valve persistence is handled automatically

## Pipeline Types

### Standard Pipeline

A standard pipeline processes requests and returns responses:

```python
class Pipeline:
    def __init__(self):
        self.type = "pipe"
        self.id = "my-pipeline"
        self.name = "My Pipeline"
        self.valves = self.Valves()

    def pipe(self, user_message: str, model_id: str, messages: list, body: dict):
        """Process the request and return response"""
        return "Processed response"
```

### Filter Pipeline

A filter pipeline can modify requests before they reach a pipeline and/or modify responses:

```python
class Pipeline:
    def __init__(self):
        self.type = "filter"
        self.id = "my-filter"
        self.name = "My Filter"
        self.valves = self.Valves()

    async def inlet(self, body: dict, user: str):
        """Modify the incoming request"""
        return body

    async def outlet(self, body: dict, user: str):
        """Modify the outgoing response"""
        return body
```

### Manifold Pipeline

A manifold pipeline can expose multiple sub-pipelines:

```python
class Pipeline:
    def __init__(self):
        self.type = "manifold"
        self.id = "my-manifold"
        self.name = "My Manifold"
        self.valves = self.Valves()

    def pipelines(self):
        """Return list of available pipelines"""
        return [
            {"id": "sub1", "name": "Sub Pipeline 1"},
            {"id": "sub2", "name": "Sub Pipeline 2"}
        ]

    def pipe(self, user_message: str, model_id: str, messages: list, body: dict):
        """Process request based on model_id which contains the sub-pipeline id"""
        if model_id == "sub1":
            return "Sub Pipeline 1 Response"
        elif model_id == "sub2":
            return "Sub Pipeline 2 Response"
```

## Resource Management Pattern

A common pattern for managing resources throughout the lifecycle:

```python
class Pipeline:
    def __init__(self):
        self.resources = {}
        self._initialize_resources()

    def _initialize_resources(self):
        """Initialize non-async resources"""
        self.resources["config"] = self._load_config()

    async def on_startup(self):
        """Initialize async resources"""
        self.resources["session"] = aiohttp.ClientSession()
        self.resources["db"] = await self._setup_database()

    async def on_shutdown(self):
        """Clean up all resources"""
        for resource in self.resources.values():
            if hasattr(resource, "close"):
                await resource.close()
```

## Error Handling

Proper error handling is crucial in lifecycle methods:

```python
async def on_startup(self):
    try:
        self.client = await self._initialize_client()
    except ConnectionError as e:
        logger.error(f"Failed to initialize client: {e}")
        # Decide if this should be fatal
        raise

async def on_shutdown(self):
    try:
        await self.client.close()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        # Generally want to continue cleanup even if errors occur
```

## Testing Lifecycle Methods

Example of testing lifecycle methods:

```python
async def test_pipeline_lifecycle():
    pipeline = Pipeline()

    # Test startup
    await pipeline.on_startup()
    assert hasattr(pipeline, 'client')

    # Test valve updates
    pipeline.valves.api_key = "new_key"
    await pipeline.on_valves_updated()
    assert pipeline.client.api_key == "new_key"

    # Test shutdown
    await pipeline.on_shutdown()
    assert pipeline.client.closed
