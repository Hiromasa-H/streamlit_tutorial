from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
import shutil
import os
from langchain_openai import ChatOpenAI

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
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def save_chunks_to_database(chunks: list,db_path: str):
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        persist_directory=db_path 
        )
    
    # vector_db.persist()
    
    return vector_db

def get_context_from_db(vector_db, query):
    # results = vector_db.similarity_search_with_relevance_score(query,k=3)
    # context = '\n\n--\n\n'.join([doc.page_content for doc, _score in results])
    # return context
    retriever = vector_db.as_retriever()
    context = retriever.invoke(query)
    return context

PROMPT = """
Answer the following questions based on the given context:
{CONTEXT}

Answer the following questions based on the given context:
{QUERY}
"""

def format_prompt(context, query):
    prompt = ChatPromptTemplate.from_template(PROMPT)
    prompt = prompt.format(CONTEXT=context, QUERY=query)
    return prompt
    
if __name__ == "__main__":
    
    model = ChatOpenAI(model="gpt-4o-mini")   
    
    documents = load_PDF("documents")
    chunks = create_chunks(documents, chunk_size=500, chunk_overlap=100)
    vector_db = save_chunks_to_database(chunks, "database")
    query = 'what is this paper about? what are the main contributions?'
    context = get_context_from_db(vector_db, query) 
    prompt = format_prompt(context, query)
    ans = model.invoke(prompt)
    print(ans)