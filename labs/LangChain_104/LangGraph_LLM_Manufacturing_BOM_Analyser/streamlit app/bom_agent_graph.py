import operator
import json
import pandas as pd
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.messages import FunctionMessage


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    dataframe: pd.DataFrame


class BomAgentGraph:
    def __init__(self):
        self.graph = None
        self.compiled_graph = None
        self._setup_model()
        self._setup_tools()
        self._define_state()
        self._create_graph()
        self._define_nodes_and_edges()

    def _setup_tools(self):
        tools = []
        self.tool_executor = ToolExecutor(tools)

    def _setup_model(self):
        model = ChatOpenAI(temperature=0, streaming=True)
        functions = [
            format_tool_to_openai_function(t) for t in self.tool_executor.tools
        ]
        self.model = model.bind_functions(functions)

    def _define_state(self):
        self.state = AgentState

    def _create_graph(self):
        self.graph = StateGraph(self.state)

    def _define_nodes_and_edges(self):
        # Define nodes
        self.graph.add_node("agent", self.call_model)
        self.graph.add_node("action", self.call_tool)

        # Set entry point
        self.graph.set_entry_point("agent")

        # Add conditional and normal edges
        self.graph.add_conditional_edges(
            "agent", self.should_continue, {"continue": "action", "end": END}
        )
        self.graph.add_edge("action", "agent")

    def call_model(self, state):
        messages = state["messages"]
        response = self.model.invoke(messages)
        return {"messages": [response]}

    def call_tool(self, state):
        messages = state["messages"]
        last_message = messages[-1]

        action = ToolInvocation(
            tool=last_message.additional_kwargs["function_call"]["name"],
            tool_input=json.loads(
                last_message.additional_kwargs["function_call"]["arguments"]
            ),
        )
        response = self.tool_executor.invoke(action)
        function_message = FunctionMessage(content=str(response), name=action.tool)
        return {"messages": [function_message]}

    def should_continue(self, state):
        messages = state["messages"]
        last_message = messages[-1]
        if "function_call" not in last_message.additional_kwargs:
            return "end"
        else:
            return "continue"

    def compile(self):
        self.compiled_graph = self.graph.compile()
        return self.compiled_graph
