import streamlit as st
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

import backend.rag as rag_module

st.set_page_config(page_title="RAG Chatbot", layout="wide")

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("📚 RAG Chatbot")

# Sidebar
with st.sidebar:
    st.header("Settings")
    num_chunks = st.slider("Context chunks", 1, 10, 3)
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Ask a question about your document..."):
    # 1. Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Retrieve and generate
                response_text = rag_module.generate_answer(user_input)
                
                # Display answer
                st.markdown(response_text)
                
                # Add to history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": response_text
                })
                
            except Exception as e:
                st.error(f"Error: {e}")