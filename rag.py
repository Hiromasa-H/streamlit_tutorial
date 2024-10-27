from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
import shutil
import os
from langchain_openai import ChatOpenAI
import chromadb

from typing import List, Dict, Any
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document


def load_PDF(path: str) -> List[Document]:
    if os.path.isdir(path):
        loader = PyPDFDirectoryLoader(path, glob="*.pdf")
        documents = loader.load()
    elif os.path.isfile(path):
        if not path.lower().endswith('.pdf'):
            raise ValueError(f"与えられたファイル：  '{path}' はPDFではありません.")
        loader = PyPDFLoader(path)
        documents = loader.load()
    else:
        raise ValueError(f"与えられたパス： '{path}' はファイルでもディレクトリでもありません。")
    return documents

def create_chunks(documents: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def init_vector_db(embedding_model:Any,db_path:str)->Chroma:
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    chromadb.api.client.SharedSystemClient.clear_system_cache()
    vector_db = Chroma(
        collection_name='rag_app_collection',
        embedding_function=embedding_model,
        persist_directory=db_path 
        )
    return vector_db

def get_context_from_db(vector_db:VectorStore, query:str, k:int=5, score_threshold:float=None)->List[Document]:
    contexts = vector_db.similarity_search_with_relevance_scores(query,
                                                                 k=k,
                                                                 score_threshold=score_threshold)
    return contexts

def format_prompt(contexts:List[Document], query:str, chat_history:List[Dict[str, str]])->str:
    PROMPT = """
    You are a helpful assistant. Answer the following questions based on the given context:
    chat history: {CHAT_HISTORY}

    context: {CONTEXT}

    Answer the following questions based on the given context:
    query: {QUERY}
    """
    prompt = ChatPromptTemplate.from_template(PROMPT)
    chat_history = '\n\n'.join([f"{message['role']}: {message['content']}" for message in chat_history])
    contexts = '\n'.join([f"CONTEXT {idx}:\n{res.page_content}" for idx, (res, _score) in enumerate(contexts)])
    prompt = prompt.format(CHAT_HISTORY=chat_history,CONTEXT=contexts, QUERY=query)
    return prompt
