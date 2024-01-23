import base64
import streamlit as st
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage, HumanMessage
from mygdrive import MyGDrive
from operator import itemgetter


def bind_and_run_llm(payload):
    image = payload["image"]
    prompt = payload["prompt"]
    bound = llm.bind(images=[image])
    return bound.invoke(prompt)


@st.cache_data
def get_service(service_account_key):
    return MyGDrive(service_account_key)


@st.cache_data
def get_files(_service: MyGDrive):
    return _service.get_files()


@st.cache_data
def get_file_contents(_service: MyGDrive, fileId: str, encoded: bool):
    return _service.get_file_contents(fileId, encoded)


st.title("Multimodal Chat")
llm = Ollama(model="bakllava")

image_prompt = PromptTemplate.from_template("{image}")
prompt = PromptTemplate.from_template("{question}")

chain = (
    {"image": itemgetter("image"), "prompt": prompt} |
    RunnableLambda(bind_and_run_llm)
)


if "messages" not in st.session_state:
    st.session_state["messages"] = [
            (AIMessage(content="How can I help you?"), False)
            ]

if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None

for msg in st.session_state.messages:
    if not msg[1]:
        st.chat_message(msg[0].type).write(msg[0].content)
    else:
        st.chat_message(msg[0].type).image(msg[0].data, width=200)


def on_upload_image(fileName, fileContents):
    st.session_state.uploaded_file = fileName
    st.session_state.uploaded_file_contents = fileContents
    st.session_state.messages.append(
            (HumanMessage(
                content=fileName,
                data=fileContents
                ), True))
    st.chat_message("user").image(fileContents, width=200)


with st.sidebar:
    if uploaded_file := st.file_uploader("Upload an image file",
                                         type=["jpg", "png"]):
        on_upload_image(uploaded_file.name, uploaded_file.getvalue())

    if gcloud_service_key_file := st.file_uploader(
            "Upload your Google Cloud Service Account Key file "
            "to access images from your Google Drive", type=["json"]
            ):
        with open(gcloud_service_key_file.name, "wb") as f:
            f.write(gcloud_service_key_file.getvalue())
        st.session_state["gcloud_service_account"] = gcloud_service_key_file.name

if "gcloud_service_account" in st.session_state.keys():
    mydrive = get_service(st.session_state["gcloud_service_account"])
    for item in get_files(mydrive):
        if item["mimeType"][0:5] == "image":
            fileId = item["id"]
            fileName = item["name"]
            contents = get_file_contents(mydrive, fileId, False)
            st.sidebar.image(contents, width=100)
            if st.sidebar.button("Use", key=fileId):
                on_upload_image(fileName, contents)

if prompt := st.chat_input():
    st.session_state.messages.append((HumanMessage(content=prompt), False))
    st.chat_message("human").write(prompt)

    response = ""
    if st.session_state.uploaded_file_contents is not None:
        data = st.session_state.uploaded_file_contents
        b64 = base64.b64encode(data).decode()

        response = chain.invoke({"question": prompt, "image": b64})
    else:
        response = "Please upload an image first"

    st.session_state.messages.append((AIMessage(content=response), False))
    st.chat_message("assistant").write(response)
