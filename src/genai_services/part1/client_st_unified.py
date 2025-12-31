import requests
import streamlit as st

st.title("FastAPI Multimodal Chatbot")

# Initialize separate message histories for each modality
if "text_messages" not in st.session_state:
    st.session_state.text_messages = []
if "audio_messages" not in st.session_state:
    st.session_state.audio_messages = []
if "image_messages" not in st.session_state:
    st.session_state.image_messages = []

# Create tabs for each modality
tab_text, tab_audio, tab_image = st.tabs(["💬 Text", "🎵 Audio", "🖼️ Image"])

# Text Generation Tab
with tab_text:
    st.header("Text Generation")

    # Display existing messages
    for message in st.session_state.text_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(
        "Write your prompt in this input field", key="text_input"
    ):
        st.session_state.text_messages.append({"role": "user", "content": prompt})

        # Call the text generation API
        response = requests.post(
            "http://localhost:8000/generate/text",
            json={"prompt": prompt, "model": "tinyllama", "temperature": 0.01},
            timeout=60,  # 60 seconds timeout
        )
        response.raise_for_status()
        # gather the response from API while treating it as plain text to ensure markdown is rendered correctly
        assistant_response = response.json()["content"]

        st.session_state.text_messages.append(
            {"role": "assistant", "content": assistant_response}
        )

        # Rerun to display the new messages
        st.rerun()

# Audio Generation Tab
with tab_audio:
    st.header("Audio Generation")

    # Display existing messages
    for message in st.session_state.audio_messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            if isinstance(content, bytes):
                st.audio(content)
            else:
                st.text(content)

    # Chat input
    if prompt := st.chat_input(
        "Write your prompt in this input field", key="audio_input"
    ):
        st.session_state.audio_messages.append({"role": "user", "content": prompt})

        # Call the audio generation API
        response = requests.get(
            "http://localhost:8000/generate/audio",
            params={"prompt": prompt},
            timeout=60,  # 60 seconds timeout
        )
        response.raise_for_status()

        assistant_response = response.content
        st.session_state.audio_messages.append(
            {"role": "assistant", "content": assistant_response}
        )

        # Rerun to display the new messages
        st.rerun()

# Image Generation Tab
with tab_image:
    st.header("Image Generation")

    # Display existing messages
    for message in st.session_state.image_messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            if isinstance(content, bytes):
                st.image(content)
            else:
                st.text(content)

    # Chat input
    if prompt := st.chat_input(
        "Write your prompt in this input field", key="image_input"
    ):
        st.session_state.image_messages.append({"role": "user", "content": prompt})

        # Call the image generation API
        response = requests.get(
            "http://localhost:8000/generate/bentoml/image",
            params={"prompt": prompt},
            timeout=60,  # 60 seconds timeout
        )
        response.raise_for_status()

        assistant_response = response.content
        st.session_state.image_messages.append(
            {"role": "assistant", "content": assistant_response}
        )

        # Rerun to display the new messages
        st.rerun()
