import streamlit as st
from rag import *
from langchain_openai import OpenAIEmbeddings
    
st.title('PDF RAG Chatbot')        

def reset_st_session():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    model = ChatOpenAI(model='gpt-4o-mini') 
    try:
        documents = load_PDF(path='documents')
    except:
        st.warning('RAGを使うためにはPDFファイルをアップロードしてください', icon="⚠️")
    else:
        chunks = create_chunks(documents=documents, chunk_size=500, chunk_overlap=50)
        embedding_model= OpenAIEmbeddings(model='text-embedding-3-small')
        vector_db = init_vector_db(embedding_model=embedding_model,db_path="database")
        vector_db.add_documents(documents=chunks)
        st.session_state.model = model
        st.session_state.vector_db = vector_db
        
        msg = 'PDFデータの準備が完了しました。'
        # st.session_state.messages.append({'role':'assistant', 'content':msg})
        st.success(msg)
    return

if 'vector_db' not in st.session_state:
    reset_st_session()
    
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

if user_prompt := st.chat_input():
    with st.chat_message('user'):
        st.markdown(user_prompt)

    st.session_state.messages.append({'role':'user', 'content':user_prompt})
    
    context = get_context_from_db(st.session_state.vector_db, user_prompt) 
    prompt,sources = format_prompt(context, user_prompt,st.session_state.messages)

    with st.chat_message('assistant'):
        response = st.write_stream(st.session_state.model.stream(prompt))
        formatted_sources = '参考文献：\n' 
        formatted_sources += '\n '.join(f"{idx+1}. {source['source']}, {source['page']}ページ" for idx,source in enumerate(sources))
        st.markdown(formatted_sources)
    st.session_state.messages.append({'role':'assistant', 'content':response})