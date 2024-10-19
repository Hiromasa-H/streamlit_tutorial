import streamlit as st
from rag import *

    
st.title('PDF RAG Chatbot')        

# initalize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
    
if 'data_prepared' not in st.session_state:
    st.session_state.data_prepared = False
    model = ChatOpenAI(model="gpt-4o-mini")   
    documents = load_PDF("documents")
    chunks = create_chunks(documents, chunk_size=1000, chunk_overlap=500)
    vector_db = save_chunks_to_database(chunks, "database")
    
    st.session_state.data_prepared = True
    st.session_state.model = model
    st.session_state.vector_db = vector_db
    
    msg = 'PDFデータの準備が完了しました。'
    st.session_state.messages.append({'role':'assistant', 'content':msg})
else:
    vector_db = st.session_state.vector_db
    model = st.session_state.model
    

    
    
# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])

if user_prompt := st.chat_input():
    with st.chat_message('user'):
        st.markdown(user_prompt)
        
    # Add user message to chat history
    st.session_state.messages.append({'role':'user', 'content':user_prompt})
    
    context = get_context_from_db(vector_db, user_prompt) 

    prompt = format_prompt(context, user_prompt,st.session_state.messages)
    print(prompt)
    # ans = model.invoke(prompt)
    # response = ans.content
    
#    model.stream(prompt)
    
    # response_chunks = []
    with st.chat_message('assistant'):
        # st.markdown(response)
        response = st.write_stream(model.stream(prompt))
        
    st.session_state.messages.append({'role':'assistant', 'content':response})