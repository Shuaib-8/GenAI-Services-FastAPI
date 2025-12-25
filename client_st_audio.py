import requests
import streamlit as st

st.title("FastAPI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, bytes):
            st.audio(content)
        else:
            st.text(content)

if prompt := st.chat_input("Write your prompt in this input field"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.text(prompt)

    response = requests.get(
        "http://localhost:8000/generate/audio",
        params={"prompt": prompt},
        timeout=60,  # 60 seconds timeout
    )
    response.raise_for_status()

    assistant_response = response.content
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )

    with st.chat_message("assistant"):
        st.audio(assistant_response)
