import streamlit as st
st.write("Hello, world!")
st.write("# Hello, world! but with markdown!")
x = st.text_input("this is a text input box")
st.write(x)

is_clicked = st.button("Click me") 

is_checked = st.checkbox("Check me")

st.link("https://www.google.com", "Google")
st.link_button("https://www.google.com", "Google")