import streamlit as st
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

import backend.rag as rag_module
import backend.retrieval as retrieval_module

st.set_page_config(page_title="RAG Bot", layout="wide")

st.title("📚 RAG Document Bot")

# Sidebar implementation
with st.sidebar:
    st.header("Settings")
    num_chunks = st.slider("Context Chunks", 1, 10, 3)
    st.markdown("""
    ℹ**System info**
    Database: LanceDB
    AI model: Google Gemini
    """)

# Main layout with columns
col1, col2 = st.columns([2, 1])

with col1:
    user_query = st.text_input("Your Question:", key="query_input")
    search_button = st.button("Search", type="primary")

with col2:
    st.markdown("### Examples")
    if st.button("What is this document about?"):
        user_query = "What is this document about?"
        search_button = True

if search_button and user_query:
    with st.spinner("Processing..."):
        try:
            # Logic
            retrieved_chunks = retrieval_module.search_db(user_query, limit=num_chunks)
            answer = rag_module.generate_answer(user_query)
            
            st.markdown("### Answer")
            st.success(answer['answer'])
            
            # Expander for sources
            with st.expander("Show Sources"):
                for i, chunk in enumerate(retrieved_chunks, 1):
                    st.markdown(f"**Source {i} - Page {chunk['page_number']}**")
                    st.text(chunk['text'])
                    st.divider()
                    
        except Exception as e:
            st.error(f"Error: {e}")