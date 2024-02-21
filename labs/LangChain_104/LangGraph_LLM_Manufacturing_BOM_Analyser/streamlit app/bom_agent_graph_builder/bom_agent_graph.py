import functools
import json
from langchain_core.messages import FunctionMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.graph import END, StateGraph
from .agent_state import AgentState
from .helpers import create_agent, agent_node, tool_node
from .custom_tools import python_repl, python_ast_repl


class BomAgentGraph:
    def __init__(self):
        self.graph = None
        self.compiled_graph = None
        self._setup_model()
        self._setup_tools()
        self._define_state()
        self._define_agents_nodes()
        self._define_tool_node()
        self._create_graph()
        self._define_nodes_and_edges()

    def _setup_model(self):
        self.model = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")

    def _setup_tools(self):

        tools = [python_ast_repl, python_repl]
        self.tool_executor = ToolExecutor(tools)

    def _define_state(self):
        self.state = AgentState

    def _define_agents_nodes(self):

        graph_traversal_agent = create_agent(
            self.model,
            [python_ast_repl],
            system_message="You should provide accurate data for the df Constructor to use.",
        )

        df_construction_agent = create_agent(
            self.model,
            [python_repl],
            system_message="You should provide accurate data for the Chart Generator to use. Any data you provide will be visible by the user.",
        )

        chart_generator_agent = create_agent(
            self.model,
            [python_repl],
            system_message="Any charts you display will be visible by the user.",
        )

        self.graph_traversal_agent_node = functools.partial(
            agent_node, agent=graph_traversal_agent, name="Graph Traverser"
        )
        self.df_construction_agent_node = functools.partial(
            agent_node, agent=df_construction_agent, name="df Constructor"
        )
        self.chart_generator_agent_node = functools.partial(
            agent_node, agent=chart_generator_agent, name="Chart Generator"
        )

    def _define_tool_node(self):
        self.tool_node = functools.partial(tool_node, tool_executor=self.tool_executor)

    def _create_graph(self):
        self.graph = StateGraph(self.state)

    def _define_nodes_and_edges(self):
        # Define nodes
        self.graph.add_node("Graph Traverser", self.graph_traversal_agent_node)
        self.graph.add_node("df Constructor", self.df_construction_agent_node)
        self.graph.add_node("Chart Generator", self.chart_generator_agent_node)

        self.graph.add_node("call_tool", self.tool_node)

        self.graph.add_conditional_edges(
            "Graph Traverser",
            self.router,
            {"continue": "df Constructor", "call_tool": "call_tool", "end": END},
        )

        self.graph.add_conditional_edges(
            "df Constructor",
            self.router,
            {"continue": "Chart Generator", "call_tool": "call_tool", "end": END},
        )

        self.graph.add_conditional_edges(
            "Chart Generator",
            self.router,
            {"continue": "Chart Generator", "call_tool": "call_tool", "end": END},
        )

        self.graph.add_conditional_edges(
            "call_tool",
            # Each agent node updates the 'sender' field
            # the tool calling node does not, meaning
            # this edge will route back to the original agent
            # who invoked the tool
            lambda x: x["sender"],
            {
                "Graph Traverser": "Graph Traverser",
                "df Constructor": "df Constructor",
                "Chart Generator": "Chart Generator",
            },
        )

        self.graph.set_entry_point("Graph Traverser")

    def router(self, state):

        messages = state["messages"]
        last_message = messages[-1]
        if "function_call" in last_message.additional_kwargs:
            # The previus agent is invoking a tool
            return "call_tool"
        if "FINAL ANSWER" in last_message.content:
            # Any agent can decide the work is done
            return "end"
        return "continue"

    def compile(self):
        self.compiled_graph = self.graph.compile()
        return self.compiled_graph
