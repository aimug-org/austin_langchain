import base64
import json
import operator
import os
import requests
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import Ollama
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    FunctionMessage
)
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.pydantic_v1 import BaseModel, Field
from langchain import hub
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvocation, ToolExecutor
from numpy import random
from typing import Optional, TypedDict, Annotated, Sequence, Dict

# default base urls for automatic 1111 and ollama
a_1111_base_url = "http://localhost:7860"
ollama_base_url = "http://localhost:11434"

# environment variable names
a_1111_env_key = "AUTOMATIC1111_HOST_URL"
ollama_env_key = "OLLAMA_HOST_URL"

# override values for automatic 1111 and ollama from
# environment variables if present
if a_1111_env_key in os.environ:
    a_1111_base_url = os.environ[a_1111_env_key]

if ollama_env_key in os.environ:
    ollama_base_url = os.environ[ollama_env_key]

# bakllava model for image to text
image_llm = Ollama(model="bakllava",
                   base_url=ollama_base_url,
                   num_predict=100)

# llama2 model for text chat
text_llm = ChatOllama(model="llama2", base_url=ollama_base_url)

# mistral 7b functioncall model for function calling
fc_llm = ChatOllama(model="klcoder/mistral-7b-functioncall",
                    format="json", num_predict=100)


# config class for automatic 1111 image generation parameters with defaults
class Config(BaseModel):
    prompt: str
    negative_prompt: str = ''
    sampler_name: str = 'DPM++ 2M Karras'
    checkpoint_name: str = 'dreamshaperXL_v21TurboDPMSDE'
    batch_size: int = 1
    steps: int = 20
    seed: Optional[int] = None
    cfg_scale: int = 7
    width: int = 512
    height: int = 512
    denoising_strength: float = 0.7
    enable_hr: bool = False
    hr_scale: int = 2
    hr_upscaler: str = '4xUltrasharp_4xUltrasharpV10'
    hr_sampler_name: str = 'DPM++ 2M Karras'
    send_images: bool = True
    save_images: bool = True


# argument schema for txt2image tool
class Txt2ImageInput(BaseModel):
    prompt: str = Field(
        description="MidJourney style prompt for image generation")


# txt2image tool
@tool("txt2image", args_schema=Txt2ImageInput)
def txt2image(prompt: str, **kwargs) -> Dict:
    (
        "An image generation tool that takes in a prompt as string "
        "and returns a json response with images encoded in base64 string. "
        "The prompt is transformed from simple English "
        "to a comma separate MidJourney image generation prompt."
    )

    config = Config(prompt=prompt, **kwargs)
    if config.seed is None:
        config.seed = int(random.normal(scale=2**32))
    response = requests.post(a_1111_base_url + "/sdapi/v1/txt2img",
                             json=config.dict()).json()
    return response


# argument schema for image2text tool
class Image2TxtInput(BaseModel):
    prompt: str = Field(description="Question regarding the image")
    image: str = Field(description="Base64 encoded image")


# image2txt tool
@tool("image2txt", args_schema=Image2TxtInput)
def image2txt(prompt: str, image: str) -> str:
    (
        "An image description tool that takes "
        "in a question about an image or a picture as a prompt "
        "and returns the answer as string"
    )

    no_image_error = (
        "No image available within context. "
        "Upload an image or generate using prompt to describe it."
    )

    try:
        if image is None or len(image) == 0:
            return no_image_error
        _ = base64.b64decode(image)
    except Exception:
        return no_image_error

    bound = image_llm.bind(images=[image])
    response: str = bound.invoke(prompt)
    return response.strip()


# function to transform tool schema for function calling model
def tool_to_definition(tool):
    args = tool.args_schema.schema()
    args = {arg: args[arg] for arg in args if arg != 'title'}
    definition = {
        'name': tool.name,
        'description': tool.description.split(" - ")[-1],
        'parameters': args
    }
    return json.dumps(definition, indent=2)


tools = [image2txt, txt2image]
tool_descriptions = "\n\n".join([tool_to_definition(tool) for tool in tools])
tool_executor = ToolExecutor(tools)


# output format for function calling chain
class OutputFormat(BaseModel):
    function: Optional[str] = Field(description="Name of the function to call")
    arguments: Optional[Dict] = Field(
        description="Arguments or parameters to pass to the function")


# prompt template for function calling chain
fc_prompt = (
    hub
    .pull("klcoder/mistral-functioncalling")
    .partial(tools=tool_descriptions)
)

# function calling chain
fc_chain = fc_prompt | fc_llm | JsonOutputParser(pydantic_object=OutputFormat)

# prompt template for chat chain
text_prompt = PromptTemplate.from_template("""
You are a helpful agent. Respond to user questions honestly and truthfully.

Human: {question}
AI: """)

# text chat chain
text_chain = text_prompt | text_llm | StrOutputParser()


# state definition for langgraph agent
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    image: Optional[str]


# node function to execute tools
def call_tool(state):
    messages = state['messages']
    last_message = messages[-1]

    if isinstance(last_message, HumanMessage):
        return {"messages": []}

    tool_input = last_message.additional_kwargs

    if "image" in state and state["image"] is not None:
        tool_input["image"] = state["image"]

    action = ToolInvocation(
        tool=last_message.name,
        tool_input=tool_input,
    )

    response = tool_executor.invoke(action)
    function_message = FunctionMessage(
        content=json.dumps(response), name=action.tool)
    return {"messages": [function_message]}


# node function to call function calling model
def call_fc_model(state):
    messages = state["messages"]
    last_message = messages[-1]

    response = fc_chain.invoke({"question": last_message.content})
    if ('name' in response
            and response['name'] in [tool.name for tool in tools]):

        args = response["arguments"]

        if "image" in state and state["image"] is not None:
            args["image"] = state["image"]
        return {"messages": [AIMessage(
                    name=response["name"],
                    content="function",
                    additional_kwargs=args
                )]}
    else:
        return {"messages": [last_message]}


# node function for chat model
def call_model(state):
    messages = state["messages"]
    last_message = messages[-1]

    response = text_chain.invoke({"question": last_message.content})
    return {"messages": [AIMessage(content=response)]}


# conditional logic to determine which edge to take based on last message
def is_function_call(state):
    messages = state["messages"]
    last_message = messages[-1]

    if isinstance(last_message, HumanMessage):
        return "human"
    if (isinstance(last_message, AIMessage)
            and last_message.content == "function"):
        return "function"
    else:
        return "end"


# langgraph agent graph definition
workflow = StateGraph(AgentState)
workflow.add_node("functions", call_fc_model)
workflow.add_node("model", call_model)
workflow.add_node("tools", call_tool)
workflow.set_entry_point("functions")
workflow.add_conditional_edges(
    "functions",
    is_function_call,
    {
        "human": "model",
        "function": "tools",
        "end": END
    }
)
workflow.add_edge("tools", END)
workflow.add_edge("model", END)
app = workflow.compile()
