import json
import functools
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

        self._define_state()
        self._define_agents_nodes()
        self._define_nodes()
        self._create_graph()
        self._define_nodes_and_edges()

    def _setup_model(self):
        self.model = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")

    def _define_state(self):
        self.state = AgentState

    def _define_nodes(self):

        def review_query(state):
            return state

        def extract_from_graph(state):
            return state

        def construct_df(state):
            return state

        def plot_df(state):
            return state

        def display_png(state):
            return state

        def handle_early_end(state):
            return state

    def _create_graph(self):
        self.graph = StateGraph(self.state)

    def _define_nodes_and_edges(self):
        # Define nodes

        self.graph.set_entry_point("review_query")

        self.graph.add_node("review_query", review_query)
        self.graph.add_node("extract_from_graph", extract_from_graph)
        self.graph.add_node("construct_df", construct_df)
        self.graph.add_node("plot_df", plot_df)
        self.graph.add_node("display_png", display_png)
        self.graph.add_node("handle_early_end", handle_early_end)

        self.graph.add_edge("handle_early_end", END)
        self.graph.add_edge("display_png", END)

        self.graph.add_conditional_edges(
            "review_query",
            review_initial_query,
            {
                True: "extract_from_graph",
                False: "handle_early_end",
            },
        )

        self.graph.add_conditional_edges(
            "extract_from_graph",
            review_extracted_graph_data,
            {
                True: "construct_df",
                False: "handle_early_end",
            },
        )

        self.graph.add_conditional_edges(
            "display_df",
            review_df_data,
            {
                True: "generate_png",
                False: "handle_early_end",
            },
        )

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

    def get_image_data(self):
        if self.compiled_graph is None:
            raise ValueError("You need to compile the graph first.")
        image_data = self.compiled_graph.get_graph().draw_png()
        return image_data
