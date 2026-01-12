import requests
import streamlit as st

st.title("LLM Wiki Web Scraper Chatbot")

# Initialize session state for message history
if "scraper_messages" not in st.session_state:
    st.session_state.scraper_messages = []

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")

    # Set the sidebar width to 400px for better readability of the sidebar
    st.markdown(
        """
    <style>
    [data-testid="stSidebar"] {
        min-width: 400px;
        max-width: 400px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.01,
        max_value=1.0,
        value=0.01,
        step=0.05,
        help="Controls randomness in text generation. Lower values are more focused, higher values are more creative.",
    )

    st.divider()

    st.markdown("""
    ### How to use:
    1. Enter a prompt with optional URLs (e.g., Wikipedia links)
    2. The scraper will extract URLs from your prompt
    3. Content from those URLs will be fetched and used to generate a response

    ### Example prompts:
    - "Summarize this article: https://en.wikipedia.org/wiki/Python"
    - "Compare these topics: https://en.wikipedia.org/wiki/Machine_learning https://en.wikipedia.org/wiki/Deep_learning"
    """)

# Display existing messages
for message in st.session_state.scraper_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Display metadata for assistant messages
        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"]
            with st.expander("Response Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Tokens", metadata.get("tokens", "N/A"))
                with col2:
                    st.metric("Model", metadata.get("model", "N/A"))

# Chat input
if prompt := st.chat_input("Write your prompt (you can include URLs to scrape)"):
    # Add user message to chat
    st.session_state.scraper_messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant message with spinner
    with st.chat_message("assistant"):
        with st.spinner("Scraping URLs and generating response..."):
            try:
                # Call the scraper API
                response = requests.post(
                    "http://localhost:8000/generate/scrape/text",
                    json={
                        "prompt": prompt,
                        "model": "tinyllama",
                        "temperature": temperature,
                    },
                    timeout=120,  # 2 minutes timeout for scraping + generation
                )
                response.raise_for_status()

                # Parse response
                response_data = response.json()
                assistant_content = response_data.get("content", "")

                # Display content
                st.markdown(assistant_content)

                # Store message with metadata
                st.session_state.scraper_messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_content,
                        "metadata": {
                            "tokens": response_data.get("tokens", 0),
                            "model": response_data.get("model", "tinyllama"),
                            "request_id": response_data.get("request_id", ""),
                            "temperature": response_data.get(
                                "temperature", temperature
                            ),
                        },
                    }
                )

                # Show success message with metadata
                with st.expander("Response Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tokens", response_data.get("tokens", "N/A"))
                    with col2:
                        st.metric("Model", response_data.get("model", "N/A"))

            except requests.exceptions.Timeout:
                error_msg = (
                    "⏱️ Request timed out. The scraping or generation took too long."
                )
                st.error(error_msg)
                st.session_state.scraper_messages.append(
                    {"role": "assistant", "content": error_msg}
                )
            except Exception as e:
                error_msg = f"❌ Unexpected error: {str(e)}"
                st.error(error_msg)
                st.session_state.scraper_messages.append(
                    {"role": "assistant", "content": error_msg}
                )

    # Rerun to display the new messages
    st.rerun()
