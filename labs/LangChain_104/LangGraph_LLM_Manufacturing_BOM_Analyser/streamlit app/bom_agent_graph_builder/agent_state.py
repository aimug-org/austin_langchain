from typing import TypedDict, Annotated, Sequence
import operator
import pandas as pd
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
