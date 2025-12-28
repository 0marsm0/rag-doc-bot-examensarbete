import streamlit as st
import sys
from datetime import datetime
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

import backend.rag as rag_module
import backend.retrieval as retrieval_module

st.set_page_config(page_title="RAG Chatbot", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .source-box {
        background-color: #f0f2f6;
        border-left: 3px solid #4CAF50;
        padding: 10px;
        margin-top: 5px;
        font-size: 0.9em;
    }
    .timestamp {
        color: #888;
        font-size: 0.8em;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.title("⚙️ Settings")
    num_chunks = st.slider("Context chunks", 1, 10, 3)
    show_sources = st.checkbox("Show Sources", value=True)

# Display history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "timestamp" in message:
             st.markdown(f"<div class='timestamp'>{message['timestamp']}</div>", unsafe_allow_html=True)

if user_input := st.chat_input("Ask a question..."):
    timestamp = datetime.now().strftime("%H:%M")
    
    # User message
    st.session_state.chat_history.append({
        "role": "user", "content": user_input, "timestamp": timestamp
    })
    with st.chat_message("user"):
        st.markdown(user_input)
        st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)

    # Assistant message
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                # Logic to get answer and sources
                retrieved_chunks = retrieval_module.search_db(user_input, limit=num_chunks)
                answer = rag_module.generate_answer(user_input)

                st.markdown(answer['answer'])
                st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)

                # Show sources
                if show_sources and retrieved_chunks:
                    with st.expander(f"View {len(retrieved_chunks)} Sources"):
                        for i, chunk in enumerate(retrieved_chunks, 1):
                            st.markdown(
                                f"<div class='source-box'>"
                                f"<strong>Source {i} - Page {chunk['page_number']}</strong><br>"
                                f"{chunk['text'][:200]}..."
                                f"</div>", 
                                unsafe_allow_html=True
                            )
                
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": answer, 
                    "timestamp": timestamp
                })
                
            except Exception as e:
                st.error(str(e))