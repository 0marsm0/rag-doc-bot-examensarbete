import streamlit as st
import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
backend_path = project_root / "backend"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))
import backend.rag as rag_module
import backend.retrieval as retrieval_module

# Page configuration
st.set_page_config(
    page_title="RAG Document Bot",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("📚 RAG Document Bot")
st.markdown("Ask questions about your document and get answers based on its content.")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    num_chunks = st.slider(
        "Context Chunks",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of relevant text sections to retrieve"
    )
    
    st.divider()
    st.markdown("### About the System")
    st.info(
        "This is a RAG (Retrieval-Augmented Generation) bot "
        "that uses LanceDB for vector search and Gemini for answer generation."
    )

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Query input
    user_query = st.text_input(
        "Your Question:",
        placeholder="E.g., What is the main conclusion?",
        key="query_input"
    )
    
    search_button = st.button("🔍 Search Answer", type="primary", use_container_width=True)

with col2:
    st.markdown("### Quick Questions")
    if st.button("What is this document about?", use_container_width=True):
        user_query = "What is this document about?"
        search_button = True
    
    if st.button("What are the requirements?", use_container_width=True):
        user_query = "What are the requirements?"
        search_button = True

# Handle search
if search_button and user_query:
    with st.spinner("Searching document..."):
        try:
            # Display user's question
            st.markdown("### 💭 Your Question")
            st.info(user_query)
            
            # Retrieve relevant chunks
            retrieved_chunks = retrieval_module.search_db(user_query, limit=num_chunks)
            
            # Generate answer
            answer = rag_module.generate_answer(user_query)
            
            # Display answer
            st.markdown("### 🤖 Answer")
            st.success(answer['answer'])
            
            # Display sources
            with st.expander("📄 Show Sources and Context"):
                if retrieved_chunks:
                    for i, chunk in enumerate(retrieved_chunks, 1):
                        st.markdown(f"**Source {i} - Page {chunk['page_number']}**")
                        st.text_area(
                            f"Text Segment {i}",
                            chunk['text'],
                            height=150,
                            key=f"chunk_{i}",
                            disabled=True
                        )
                        st.divider()
                else:
                    st.warning("No relevant text chunks found.")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

elif search_button:
    st.warning("⚠️ Please enter a question first.")

# Chat history (for future use)
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>Powered by LanceDB, Gemini & Streamlit | RAG Document Bot v0.1.0</small>
    </div>
    """,
    unsafe_allow_html=True
)