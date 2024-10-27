import streamlit as st
import os
from langchain_openai import ChatOpenAI
from rag import *
import chromadb
from streamlit_js_eval import streamlit_js_eval
from app import reset_st_session

uploaded_files = st.file_uploader("ファイルをアップロード",
                                 accept_multiple_files=True)

if len(uploaded_files)!=0:
    for uploaded_file in uploaded_files:
        with open(os.path.join("documents",uploaded_file.name),"wb") as f:
            f.write(uploaded_file.getbuffer())
    reset_st_session()
    # if 'messages' not in st.session_state:
    #     st.session_state.messages = []
    # model = ChatOpenAI(model="gpt-4o-mini")   
    # documents = load_PDF("documents")
    # chromadb.api.client.SharedSystemClient.clear_system_cache()
    # chunks = create_chunks(documents, chunk_size=1000, chunk_overlap=500)
    # vector_db = save_chunks_to_database(chunks, "database")
    
    # st.session_state.model = model
    # st.session_state.vector_db = vector_db
    
    msg = 'PDFデータの更新が完了しました。'
    st.session_state.messages.append({'role':'assistant', 'content':msg})

st.write('#### ファイル一覧')
files_to_remove = []
if len(os.listdir('documents'))!=0:
    for file_name in os.listdir('documents'):
        remove_file = st.checkbox(file_name)
        if remove_file:
            files_to_remove.append(file_name)

if st.button("選択したファイルを削除",key='delete_files'):
    for file in files_to_remove:
        os.remove(f'documents/{file}')
    streamlit_js_eval(js_expressions="parent.window.location.reload()")

    
