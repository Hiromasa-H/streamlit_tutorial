import streamlit as st
from rag import *
from langchain_openai import OpenAIEmbeddings
import chromadb
from typing import List, Dict
    
st.title('PDF RAG Chatbot')        

def reset_st_session():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    model = ChatOpenAI(model='gpt-4o-mini') 
    documents = load_PDF(path='documents')
    if len(documents) == 0:
        st.warning('RAGを使うためにはファイルをアップロードしてください', icon="⚠️")
    else:
        chunks = create_chunks(documents=documents, chunk_size=500, chunk_overlap=50)
        embedding_model= OpenAIEmbeddings(model='text-embedding-3-small')
        vector_db = init_vector_db(embedding_model=embedding_model,db_path="database")
        vector_db.add_documents(documents=chunks)
        st.session_state.model = model
        st.session_state.vector_db = vector_db
        
        msg = 'PDFデータの準備が完了しました。'
        st.session_state.messages.append({'role':'assistant', 'content':msg})
    return

if 'vector_db' not in st.session_state:
    reset_st_session()
    

    
    
# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

if user_prompt := st.chat_input():
    with st.chat_message('user'):
        st.markdown(user_prompt)
        
    # Add user message to chat history
    st.session_state.messages.append({'role':'user', 'content':user_prompt})
    
    context = get_context_from_db(st.session_state.vector_db, user_prompt) 

    prompt = format_prompt(context, user_prompt,st.session_state.messages)
    print(prompt)

    with st.chat_message('assistant'):
        response = st.write_stream(st.session_state.model.stream(prompt))
        
    st.session_state.messages.append({'role':'assistant', 'content':response})