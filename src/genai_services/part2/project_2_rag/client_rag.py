from typing import Any

import requests
import streamlit as st
from requests import Response

st.title("FastAPI PDF ChatBot")

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
