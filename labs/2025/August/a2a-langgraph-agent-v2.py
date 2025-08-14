"""
A2A Protocol Testing Agent V2 - Comprehensive Testing Suite
===========================================================

A modular, elegant testing framework for Agent-to-Agent (A2A) Protocol implementations.
Tests blog capabilities, caching, performance, and protocol compliance.

FEATURES:
---------
• Individual method testing for targeted debugging
• Comprehensive test suite with detailed reporting  
• Caching header validation (ETag, Cache-Control)
• Performance metrics for each endpoint
• Support for individual and unified endpoints
• Rich console output with color-coded results

REQUIREMENTS:
------------
• Python 3.8+
• API Key: Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable
• Network access to target A2A implementation

QUICK START:
-----------
1. Install dependencies:
   pip install requests langchain-core langchain-openai langchain-anthropic langgraph rich

2. Set your API key:
   export OPENAI_API_KEY="your-key-here"

3. Run tests:
   python a2a-langgraph-agent-v2.py https://example.com --comprehensive

USAGE EXAMPLES:
--------------
# Basic discovery (default mode)
python a2a-langgraph-agent-v2.py https://example.com

# Full comprehensive testing
python a2a-langgraph-agent-v2.py https://example.com --comprehensive

# Test specific method
python a2a-langgraph-agent-v2.py https://example.com --test-method blog.list_posts

# Test all methods individually  
python a2a-langgraph-agent-v2.py https://example.com --test-all

# Check caching implementation
python a2a-langgraph-agent-v2.py https://example.com --test-caching

# Just discover capabilities
python a2a-langgraph-agent-v2.py https://example.com --discover

A2A PROTOCOL METHODS TESTED:
---------------------------
• blog.list_posts - List blog posts with pagination
• blog.get_post - Retrieve individual post by ID
• blog.search_posts - Search posts by query
• blog.get_metadata - Get blog metadata
• blog.get_author_info - Get author information

EXIT CODES:
----------
0 - All tests passed
1 - Some tests failed or API key missing
2 - Connection or discovery failed

Author: Colin McNamara
License: MIT
Version: 2.0.0
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, TypedDict, Sequence, Callable
from dataclasses import dataclass
from enum import Enum
import os
import uuid

import requests
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# ===== Data Classes for Better Structure =====
@dataclass
class TestResult:
    """Structured test result"""
    method: str
    success: bool
    response_time: float
    status_code: int
    response_data: Optional[Dict] = None
    error: Optional[str] = None
    headers: Optional[Dict] = None

@dataclass
class A2AEndpoint:
    """A2A endpoint configuration"""
    base_url: str
    service_endpoint: Optional[str] = None
    individual_endpoints: Optional[Dict[str, str]] = None
    capabilities: List[str] = None
    
    def get_url_for_method(self, method: str) -> str:
        """Get the appropriate URL for a method"""
        if self.individual_endpoints and method in self.individual_endpoints:
            return f"{self.base_url.rstrip('/')}{self.individual_endpoints[method]}"
        endpoint = self.service_endpoint or '/api/a2a/service'
        return f"{self.base_url.rstrip('/')}{endpoint}"

# ===== Base Test Class =====
class A2AMethodTest:
    """Base class for A2A method tests"""
    
    def __init__(self, endpoint: A2AEndpoint):
        self.endpoint = endpoint
        
    def execute_request(self, method: str, params: Optional[Dict] = None) -> TestResult:
        """Execute a single A2A request and return structured result"""
        url = self.endpoint.get_url_for_method(method)
        
        # For individual endpoints, don't include the method field
        using_individual = self.endpoint.individual_endpoints and method in self.endpoint.individual_endpoints
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "params": params or {}
        }
        
        # Only add method field if not using individual endpoint
        if not using_individual:
            payload["method"] = method
        
        start_time = time.time()
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            elapsed = (time.time() - start_time) * 1000
            
            response_data = response.json() if response.status_code == 200 else None
            
            return TestResult(
                method=method,
                success=response.status_code == 200 and 'result' in (response_data or {}),
                response_time=round(elapsed, 2),
                status_code=response.status_code,
                response_data=response_data,
                headers=dict(response.headers)
            )
        except Exception as e:
            return TestResult(
                method=method,
                success=False,
                response_time=(time.time() - start_time) * 1000,
                status_code=0,
                error=str(e)
            )

# ===== Specific Test Methods =====
@tool
def test_blog_list_posts(base_url: str, limit: int = 5) -> str:
    """Test blog.list_posts method with pagination"""
    endpoint = _get_endpoint(base_url)
    test = A2AMethodTest(endpoint)
    
    result = test.execute_request("blog.list_posts", {"limit": limit})
    
    if result.success:
        posts = result.response_data['result'].get('posts', [])
        return f"""✅ blog.list_posts PASSED
- Response time: {result.response_time}ms
- Posts returned: {len(posts)}
- First post: {posts[0]['title'][:50] if posts else 'None'}...
- Has pagination: {'total' in result.response_data['result']}"""
    else:
        return f"""❌ blog.list_posts FAILED
- Error: {result.error or f'Status {result.status_code}'}
- Response time: {result.response_time}ms"""

@tool
def test_blog_get_post(base_url: str, post_id: Optional[str] = None) -> str:
    """Test blog.get_post method with real or provided post ID"""
    endpoint = _get_endpoint(base_url)
    test = A2AMethodTest(endpoint)
    
    # Get a real post ID if not provided
    if not post_id:
        list_result = test.execute_request("blog.list_posts", {"limit": 1})
        if list_result.success and list_result.response_data:
            posts = list_result.response_data['result'].get('posts', [])
            if posts:
                post_id = posts[0].get('id')
    
    if not post_id:
        return "⚠️ blog.get_post SKIPPED - No post ID available"
    
    # Use 'id' parameter, not 'slug'
    result = test.execute_request("blog.get_post", {"id": post_id})
    
    if result.success:
        post = result.response_data['result']
        return f"""✅ blog.get_post PASSED
- Response time: {result.response_time}ms
- Post title: {post.get('title', 'N/A')[:50]}...
- Content length: {len(post.get('content', ''))} chars
- Has metadata: {'_a2a' in post}"""
    else:
        return f"""❌ blog.get_post FAILED
- Error: {result.error or f'Status {result.status_code}'}
- Post ID tested: {post_id}"""

@tool
def test_blog_search_posts(base_url: str, query: str = "AI", limit: int = 3) -> str:
    """Test blog.search_posts method"""
    endpoint = _get_endpoint(base_url)
    test = A2AMethodTest(endpoint)
    
    result = test.execute_request("blog.search_posts", {"query": query, "limit": limit})
    
    if result.success:
        posts = result.response_data['result'].get('posts', [])
        post_list = '\n'.join([f"  - {p['title'][:40]}..." for p in posts[:3]])
        return f"""✅ blog.search_posts PASSED
- Response time: {result.response_time}ms
- Query: "{query}"
- Posts found: {len(posts)}
{post_list if posts else '  - No posts found'}"""
    else:
        return f"""❌ blog.search_posts FAILED
- Error: {result.error or f'Status {result.status_code}'}
- Query tested: "{query}" """

@tool
def test_blog_get_metadata(base_url: str) -> str:
    """Test blog.get_metadata method"""
    endpoint = _get_endpoint(base_url)
    test = A2AMethodTest(endpoint)
    
    result = test.execute_request("blog.get_metadata")
    
    if result.success:
        metadata = result.response_data['result']
        return f"""✅ blog.get_metadata PASSED
- Response time: {result.response_time}ms
- Total posts: {metadata.get('totalPosts', 'N/A')}
- Tags count: {len(metadata.get('tags', []))}
- Latest post: {metadata.get('latestPost', {}).get('title', 'N/A')[:40] if metadata.get('latestPost') else 'N/A'}..."""
    else:
        return f"""❌ blog.get_metadata FAILED
- Error: {result.error or f'Status {result.status_code}'}"""

@tool
def test_blog_get_author_info(base_url: str) -> str:
    """Test blog.get_author_info method"""
    endpoint = _get_endpoint(base_url)
    test = A2AMethodTest(endpoint)
    
    result = test.execute_request("blog.get_author_info")
    
    if result.success:
        author = result.response_data['result']
        return f"""✅ blog.get_author_info PASSED
- Response time: {result.response_time}ms
- Name: {author.get('name', 'N/A')}
- Has bio: {'bio' in author and len(author['bio']) > 0}
- Has social links: {'social' in author}"""
    else:
        return f"""❌ blog.get_author_info FAILED
- Error: {result.error or f'Status {result.status_code}'}"""

@tool
def test_caching_headers(base_url: str) -> str:
    """Test caching headers implementation"""
    endpoint = _get_endpoint(base_url)
    test = A2AMethodTest(endpoint)
    
    # Test a cacheable endpoint
    result = test.execute_request("blog.get_metadata")
    
    if not result.success:
        return f"❌ Cannot test caching - endpoint failed: {result.error}"
    
    headers = result.headers or {}
    has_etag = 'etag' in headers or 'ETag' in headers
    has_cache = 'cache-control' in headers or 'Cache-Control' in headers
    
    etag = headers.get('etag') or headers.get('ETag')
    cache_control = headers.get('cache-control') or headers.get('Cache-Control')
    
    if has_etag:
        # Test conditional request
        url = endpoint.get_url_for_method("blog.get_metadata")
        response = requests.post(
            url,
            json={"jsonrpc": "2.0", "method": "blog.get_metadata", "id": 1},
            headers={"If-None-Match": etag, "Content-Type": "application/json"}
        )
        conditional_works = response.status_code == 304
    else:
        conditional_works = False
    
    return f"""Caching Header Analysis:
- ETag present: {'✅' if has_etag else '❌'}
  {f'  Value: {etag}' if has_etag else '  Recommendation: Implement ETag generation'}
- Cache-Control present: {'✅' if has_cache else '❌'}
  {f'  Value: {cache_control}' if has_cache else '  Recommendation: Add Cache-Control headers'}
- Conditional requests: {'✅ Working (304 response)' if conditional_works else '❌ Not working'}
- Overall: {'✅ Properly implemented' if has_etag and conditional_works else '⚠️ Needs improvement'}"""

@tool
def run_comprehensive_a2a_test(base_url: str) -> str:
    """Run all A2A tests comprehensively with detailed reporting"""
    results = []
    
    # Run all tests
    tests = [
        ("Discovery", discover_a2a_capabilities_v2, {}),
        ("List Posts", test_blog_list_posts, {"limit": 3}),
        ("Get Post", test_blog_get_post, {}),
        ("Search Posts", test_blog_search_posts, {"query": "AI"}),
        ("Get Metadata", test_blog_get_metadata, {}),
        ("Get Author", test_blog_get_author_info, {}),
        ("Caching", test_caching_headers, {})
    ]
    
    console.print("\n[bold cyan]Running Comprehensive A2A Tests[/bold cyan]\n")
    
    for test_name, test_func, params in tests:
        console.print(f"Testing {test_name}...")
        result = test_func.invoke({"base_url": base_url, **params})
        results.append(result)
        
    # Generate summary
    passed = sum(1 for r in results if '✅' in r)
    failed = sum(1 for r in results if '❌' in r)
    warnings = sum(1 for r in results if '⚠️' in r)
    
    summary = f"""
{'='*60}
COMPREHENSIVE A2A TEST RESULTS
{'='*60}

{chr(10).join(results)}

{'='*60}
SUMMARY
{'='*60}
Tests Passed: {passed}
Tests Failed: {failed}
Tests with Warnings: {warnings}
Overall Score: {(passed / len(results) * 100):.0f}%
"""
    
    return summary

# ===== Helper Functions =====
def _get_endpoint(base_url: str) -> A2AEndpoint:
    """Get endpoint configuration from agent.json"""
    try:
        url = f"{base_url.rstrip('/')}/.well-known/agent.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            card = response.json()
            return A2AEndpoint(
                base_url=base_url,
                service_endpoint=card.get('serviceEndpoint'),
                individual_endpoints=card.get('serviceEndpoints'),
                capabilities=_extract_capabilities(card)
            )
    except:
        pass
    
    # Return default
    return A2AEndpoint(base_url=base_url)

def _extract_capabilities(card: Dict) -> List[str]:
    """Extract capabilities from various formats"""
    capabilities = card.get('capabilities', [])
    if not capabilities and 'skills' in card:
        capabilities = [skill.get('method', skill.get('id')) for skill in card['skills']]
    if not capabilities and 'serviceEndpoints' in card:
        capabilities = list(card['serviceEndpoints'].keys())
    return capabilities

@tool
def discover_a2a_capabilities_v2(base_url: str) -> str:
    """Discover A2A capabilities with better structure"""
    try:
        endpoint = _get_endpoint(base_url)
        url = f"{base_url.rstrip('/')}/.well-known/agent.json"
        response = requests.get(url, timeout=10)
        card = response.json()
        
        return f"""✅ A2A Discovery Successful
- Name: {card.get('name', 'Unknown')}
- Version: {card.get('version', 'Unknown')}
- Protocol: {card.get('protocolVersion', 'Unknown')}
- Capabilities: {len(endpoint.capabilities)} found
  {chr(10).join(f'  • {cap}' for cap in endpoint.capabilities[:5])}
- Implementation: {'Individual endpoints' if endpoint.individual_endpoints else 'Single endpoint'}"""
    except Exception as e:
        return f"❌ A2A Discovery Failed: {str(e)}"

# ===== Agent State and Graph Construction =====
class AgentState(TypedDict):
    """State for the A2A testing agent"""
    messages: Sequence[BaseMessage]
    base_url: str
    test_results: Dict[str, Any]
    analysis: Dict[str, Any]
    recommendations: List[str]
    next_action: str
    test_mode: str  # Added to track test mode

async def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor that orchestrates testing"""
    model_name = os.getenv("LLM_MODEL", "gpt-4")
    
    if "claude" in model_name.lower():
        model = ChatAnthropic(model_name=model_name)
    else:
        model = ChatOpenAI(model_name=model_name)
    
    tools = [
        discover_a2a_capabilities_v2,
        test_blog_list_posts,
        test_blog_get_post,
        test_blog_search_posts,
        test_blog_get_metadata,
        test_blog_get_author_info,
        test_caching_headers,
        run_comprehensive_a2a_test
    ]
    
    model_with_tools = model.bind_tools(tools)
    
    # Get test mode from state
    test_mode = state.get("test_mode", "comprehensive")
    
    if test_mode == "comprehensive":
        system_prompt = """You are an A2A Protocol testing expert. 
        
Your testing strategy for COMPREHENSIVE mode:
1. First run discover_a2a_capabilities_v2 to understand the implementation
2. Then run run_comprehensive_a2a_test to test all methods at once
3. Analyze the results and provide recommendations

Be thorough and systematic."""
    
    elif test_mode == "discover":
        system_prompt = """You are an A2A Protocol testing expert.
        
For DISCOVERY mode:
1. You MUST run discover_a2a_capabilities_v2 to understand the implementation
2. After getting the results, provide a summary
3. Do NOT run other tests - just discovery

Focus on capability discovery only. Use the tool first, then summarize."""
    
    elif test_mode == "caching":
        system_prompt = """You are an A2A Protocol testing expert.
        
For CACHING mode:
1. First discover capabilities 
2. Then run test_caching_headers to validate caching implementation
3. Provide specific recommendations for caching improvements

Focus on HTTP caching validation."""
    
    elif test_mode.startswith("method:"):
        method_name = test_mode.split(":", 1)[1]
        method_tool_map = {
            "blog.list_posts": "test_blog_list_posts",
            "blog.get_post": "test_blog_get_post",
            "blog.search_posts": "test_blog_search_posts",
            "blog.get_metadata": "test_blog_get_metadata",
            "blog.get_author_info": "test_blog_get_author_info"
        }
        tool_name = method_tool_map.get(method_name, "")
        system_prompt = f"""You are an A2A Protocol testing expert.
        
For SPECIFIC METHOD testing of {method_name}:
1. First discover capabilities
2. Test the specific method using {tool_name}
3. Provide detailed analysis of this method

Focus only on testing {method_name}."""
    
    else:  # test_all
        system_prompt = """You are an A2A Protocol testing expert.
        
For TEST ALL mode:
1. First run discover_a2a_capabilities_v2
2. Test each method individually: test_blog_list_posts, test_blog_get_post, test_blog_search_posts, test_blog_get_metadata, test_blog_get_author_info
3. Test caching headers
4. Provide detailed per-method analysis

Test methods one by one for detailed results."""
    
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = await model_with_tools.ainvoke(messages)
    
    state["messages"].append(response)
    state["next_action"] = "use_tools" if response.tool_calls else "analyze"
    
    return state

async def tool_node(state: AgentState) -> AgentState:
    """Execute tools based on agent's decision"""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, 'tool_calls'):
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            # Add base_url if not present
            if "base_url" not in tool_args and state.get("base_url"):
                tool_args["base_url"] = state["base_url"]
            
            tool_map = {
                "discover_a2a_capabilities_v2": discover_a2a_capabilities_v2,
                "test_blog_list_posts": test_blog_list_posts,
                "test_blog_get_post": test_blog_get_post,
                "test_blog_search_posts": test_blog_search_posts,
                "test_blog_get_metadata": test_blog_get_metadata,
                "test_blog_get_author_info": test_blog_get_author_info,
                "test_caching_headers": test_caching_headers,
                "run_comprehensive_a2a_test": run_comprehensive_a2a_test
            }
            
            if tool_name in tool_map:
                result = tool_map[tool_name].invoke(tool_args)
                state["test_results"][tool_name] = result
                state["messages"].append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_id
                    )
                )
    
    state["next_action"] = "supervisor"
    return state

async def analyzer_node(state: AgentState) -> AgentState:
    """Analyze test results and generate final summary"""
    model_name = os.getenv("LLM_MODEL", "gpt-4")
    
    if "claude" in model_name.lower():
        model = ChatAnthropic(model_name=model_name)
    else:
        model = ChatOpenAI(model_name=model_name)
    
    # Only run analysis if we have test results
    if not state.get("test_results"):
        state["next_action"] = "end"
        return state
    
    analysis_prompt = f"""Based on the A2A testing performed, provide:
1. A summary of what's working well
2. Any issues or failures found
3. Specific recommendations for improvements
4. Overall implementation grade (A-F)

Be concise and actionable."""
    
    response = await model.ainvoke([
        SystemMessage(content="You are an A2A Protocol expert providing final analysis."),
        HumanMessage(content=analysis_prompt)
    ])
    
    state["analysis"]["summary"] = response.content
    state["messages"].append(response)
    state["next_action"] = "end"
    
    return state

# ===== Graph Construction =====
def build_testing_graph():
    """Build the LangGraph workflow for A2A testing"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("analyzer", analyzer_node)
    
    # Define routing function
    def route_supervisor(state: AgentState) -> str:
        return state["next_action"]
    
    # Add conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "use_tools": "tools",
            "analyze": "analyzer",
            "end": END
        }
    )
    
    # Add edges
    workflow.add_edge("tools", "supervisor")
    workflow.add_edge("analyzer", END)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add memory
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="a2a-test",
        description="""
A2A Protocol Testing Agent V2 - Comprehensive Testing Suite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test Agent-to-Agent (A2A) Protocol implementations for compliance,
performance, and functionality. Validates blog methods, caching headers,
and protocol adherence.

Requires: OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable""",
        epilog="""
EXAMPLES:
━━━━━━━━━
  Quick discovery check:
    %(prog)s https://example.com --discover
    
  Full test suite (recommended):
    %(prog)s https://example.com --comprehensive
    
  Debug specific method:
    %(prog)s https://example.com --test-method blog.get_post
    
  Test caching implementation:
    %(prog)s https://example.com --test-caching
    
  Test all methods with individual reports:
    %(prog)s https://example.com --test-all

AVAILABLE TEST METHODS:
━━━━━━━━━━━━━━━━━━━━━━
  • blog.list_posts    - List blog posts with pagination support
  • blog.get_post      - Retrieve individual post by ID
  • blog.search_posts  - Search posts by query string
  • blog.get_metadata  - Get blog metadata and statistics
  • blog.get_author_info - Get author information and bio

ENVIRONMENT SETUP:
━━━━━━━━━━━━━━━━━
  export OPENAI_API_KEY="sk-..."       # For OpenAI models
  export ANTHROPIC_API_KEY="sk-ant..." # For Claude models
  
OUTPUT INDICATORS:
━━━━━━━━━━━━━━━━━
  ✅ Test passed successfully
  ❌ Test failed with errors
  ⚠️  Warning or needs improvement
  
For more details, see the script header documentation.""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "url", 
        help="Base URL of the A2A implementation to test (e.g., https://example.com)"
    )
    
    parser.add_argument(
        "--comprehensive", "-c", 
        action="store_true", 
        help="Run complete test suite with summary report (tests all methods, caching, and performance)"
    )
    
    parser.add_argument(
        "--test-method", "-m", 
        metavar="METHOD",
        help="Test a specific A2A method (e.g., blog.list_posts, blog.get_post)"
    )
    
    parser.add_argument(
        "--test-all", "-a", 
        action="store_true",
        help="Test all methods individually with detailed output for each"
    )
    
    parser.add_argument(
        "--test-caching", 
        action="store_true",
        help="Test caching headers only (ETag, Cache-Control, conditional requests)"
    )
    
    parser.add_argument(
        "--discover", "-d", 
        action="store_true",
        help="Only discover and display A2A capabilities without testing"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 2.0.0"
    )
    
    args = parser.parse_args()
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error: Please set OPENAI_API_KEY or ANTHROPIC_API_KEY[/red]")
        exit(1)
    
    # Enable LangSmith tracing if configured
    if os.getenv("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "a2a-testing")
        console.print("[dim]LangSmith tracing enabled[/dim]")
    
    # Determine test mode from arguments
    test_mode = "basic"  # default
    if args.comprehensive:
        test_mode = "comprehensive"
    elif args.test_method:
        test_mode = f"method:{args.test_method}"
    elif args.test_all:
        test_mode = "test_all"
    elif args.test_caching:
        test_mode = "caching"
    elif args.discover:
        test_mode = "discover"
    
    # Build the LangGraph agent
    app = build_testing_graph()
    
    # Create initial state
    initial_state = AgentState(
        messages=[HumanMessage(content=f"Please test the A2A implementation at {args.url} in {test_mode} mode")],
        base_url=args.url,
        test_results={},
        analysis={},
        recommendations=[],
        next_action="supervisor",
        test_mode=test_mode
    )
    
    # Configure thread for memory
    thread_id = f"a2a-test-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Print header based on mode
    mode_titles = {
        "comprehensive": "Running Comprehensive A2A Test Suite (via LangGraph)",
        "discover": "Discovering A2A Capabilities (via LangGraph)",
        "caching": "Testing Caching Headers (via LangGraph)",
        "test_all": "Testing All Methods Individually (via LangGraph)",
        "basic": "A2A Protocol Testing - Basic Mode (via LangGraph)"
    }
    
    if test_mode.startswith("method:"):
        console.print(f"[bold cyan]Testing method: {test_mode.split(':', 1)[1]} (via LangGraph)[/bold cyan]\n")
    else:
        console.print(f"[bold cyan]{mode_titles.get(test_mode, 'A2A Testing')}[/bold cyan]\n")
    
    # Run the agent graph asynchronously
    async def run_graph():
        async for event in app.astream(initial_state, config):
            # Process events from graph nodes
            if "tools" in event:
                state = event["tools"]
                # Show tool results as they complete
                if state.get("messages"):
                    for msg in state["messages"]:
                        if isinstance(msg, ToolMessage):
                            # Only print if we haven't seen this result yet
                            if msg.content not in printed_results:
                                console.print(msg.content)
                                printed_results.add(msg.content)
            
            elif "supervisor" in event:
                state = event["supervisor"]
                # Check if supervisor has messages to display
                if state.get("messages"):
                    last_msg = state["messages"][-1]
                    if isinstance(last_msg, AIMessage) and not hasattr(last_msg, 'tool_calls'):
                        console.print(f"\n[green]Agent Analysis:[/green] {last_msg.content}")
            
            elif "analyzer" in event:
                state = event["analyzer"]
                if state.get("analysis", {}).get("summary"):
                    console.print("\n[bold]Final Analysis:[/bold]")
                    console.print(state["analysis"]["summary"])
    
    # Track printed results to avoid duplicates
    printed_results = set()
    
    # Run the async function
    asyncio.run(run_graph())
    
    if test_mode == "basic":
        console.print("\n[dim]Tip: Use --comprehensive for full testing[/dim]")
        console.print("[dim]     Use --help to see all options[/dim]")