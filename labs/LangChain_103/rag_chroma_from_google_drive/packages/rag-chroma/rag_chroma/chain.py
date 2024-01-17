import os
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import GoogleDriveLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableParallel, RunnablePassthrough


def create_chain(folder_id):
    loader = GoogleDriveLoader(
        folder_id=folder_id,
        recursive=False,
        # we need to use service_account_key to set google credentials because we're using docker to build the api. Langchain docs on GoogleDriveLoader makes no mention of this. Solution found here: https://github.com/langchain-ai/langchain/issues/8755
        file_types=["document", "sheet", "pdf"],
        service_account_key=os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
    )
    data = loader.load()

    print("data: ", data)

    # Split
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000, chunk_overlap=0, separators=[" ", ",", "\n"]
    )
    all_splits = text_splitter.split_documents(data)

    # Add to vectorDB
    vectorstore = Chroma.from_documents(
        documents=all_splits,
        collection_name="rag-chroma",
        embedding=OpenAIEmbeddings(),
    )
    retriever = vectorstore.as_retriever()

    # RAG prompt
    template = """
    Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # LLM
    model = ChatOpenAI()

    # RAG chain
    chain = (
        RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
        | prompt
        | model
        | StrOutputParser()
    )

    # Add typing for input
    class Question(BaseModel):
        __root__: str

    chain = chain.with_types(input_type=Question)

    return chain
