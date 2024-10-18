from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

import os

def load_PDF(path: str) -> list:
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

def create_chunks(documents: list, chunk_size: int, chunk_overlap: int) -> list:
    text_splitter = RecursiveTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split(documents)
    return chunks

def save_chunks_to_database(chunks: list,db_path: str):
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    
    vector_db = Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(),
        persist_directory=db_path 
        )
    
    vector_db.persist()
    
    return vector_db

if __name__ == "__main__":
    documents = load_PDF("documents")
    chunks = create_chunks(documents, chunk_size=500, chunk_overlap=100)
    save_chunks_to_database(chunks, "database")