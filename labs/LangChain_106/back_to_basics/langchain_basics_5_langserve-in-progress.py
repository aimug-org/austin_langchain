#!/usr/bin/env python

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.messages import BaseMessage
from langserve import add_routes
from fastapi import FastAPI

# Load Retriever
loader = WebBaseLoader("https://www.austinchronicle.com/events")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
embeddings = OpenAIEmbeddings()
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()

# Create our tools
retriever_tool = create_retriever_tool(
    retriever,
    "austin_events_search",
    "Search for information about events in Austin. For any questions about austin events, you may use this tool",
)

search = DuckDuckGoSearchRun()
tools = [retriever_tool, search]


# Create our agent
prompt = hub.pull("hwchase17/openai-functions-agent")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# App definition 
app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple API for our LangChain Quickstart",
)

# Add our chain routes
class Input(BaseModel):
    input: str
    chat_history: List[BaseMessage] = Field(
    ...,
    extra={"widget": {"type": "chat", "input": "location"}},    
    )

class Output(BaseModel):
    output: str

add_routes(
    app,
    agent_executor.with_types(input_type=Input, output_type=Output),
    path="/agent",
)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="localhost", port=8000)