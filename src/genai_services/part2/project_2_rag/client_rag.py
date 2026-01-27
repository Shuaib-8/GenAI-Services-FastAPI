from typing import Any

import requests
import streamlit as st
from requests import Response

st.title("FastAPI PDF ChatBot")

if "rag_messages" not in st.session_state:
    st.session_state.rag_messages = []

st.write("Upload a PDF file to get started")
file = st.file_uploader("Upload a PDF file", type=["pdf"])

if st.button("Submit"):
    if file is not None:
        files: dict[str, tuple[Any, Any, str]] = {"file": (file.name, file, file.type)}
        response: Response = requests.post(
            "http://localhost:8000/upload", files=files, timeout=30
        )
        st.write(response.text)
    else:
        st.write("Please upload a PDF file")

# Display existing messages
for message in st.session_state.rag_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# chat input
if prompt := st.chat_input("Write your prompt"):
    st.session_state.rag_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            try:
                response = requests.post(
                    "http://localhost:8000/generate/text",
                    json={
                        "prompt": prompt,
                        "model": "tinyllama",
                        "temperature": 0.01,
                    },
                    timeout=120,
                )
                response.raise_for_status()
                response_data = response.json()
                assistant_content = response_data.get("content", "")

                st.markdown(assistant_content)
                st.session_state.rag_messages.append(
                    {"role": "assistant", "content": assistant_content}
                )
            except requests.exceptions.Timeout:
                error_msg = "⏱️ Request timed out. The generation took too long."
                st.error(error_msg)
                st.session_state.rag_messages.append(
                    {"role": "assistant", "content": error_msg}
                )
            except Exception as e:
                error_msg = f"❌ Unexpected error: {str(e)}"
                st.error(error_msg)
                st.session_state.rag_messages.append(
                    {"role": "assistant", "content": error_msg}
                )

    st.rerun()
