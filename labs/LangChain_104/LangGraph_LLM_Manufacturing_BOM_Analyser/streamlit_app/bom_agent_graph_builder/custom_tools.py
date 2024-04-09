from typing import Annotated, Any
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_experimental.tools.python.tool import PythonAstREPLTool
import streamlit as st
from bom_handler import BOMGraph
import pandas as pd
from moc_data.fake_data_df import fake_data_df


# Warning: This executes code locally, which can be unsafe when not sandboxed
@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."]
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        repl = PythonREPL()
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return f"Succesfully executed:\n```python\n{code}\n```\nStdout: {result}"


# Warning: This executes code locally, which can be unsafe when not sandboxed
@tool
def python_ast_repl(
    code: Annotated[str, "The python code to execute to generate your chart."],
    # locals: Annotated[
    #     dict[str, Any], "The local variables to use when executing the code."
    # ],
):
    """
    Use this to execute python code to traverse the provided networkx graph on the bom data. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user.
    """
    df = pd.DataFrame(fake_data_df)
    graph = BOMGraph()
    graph.update_graph_with_bom_data(df)

    try:
        tool = PythonAstREPLTool(locals=graph.G)
        result = tool._run(code)
        return f"Succesfully executed:\n```python\n{code}\n```\nResult: {result}"
    except BaseException as e:
        return f"Error: {str(e)}"
