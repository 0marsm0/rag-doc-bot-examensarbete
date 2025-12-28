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

st.title("RAG Document Bot")

user_query = st.text_input("Your Question:")

# Slider for amount of chunks
num_chunks = st.slider("Number of sources to use", 1, 5, 3)

if st.button("Search Answer"):
    if user_query:
        with st.spinner("Searching database..."):
            # 1. Retrieve context
            retrieved_chunks = retrieval_module.search_db(user_query, limit=num_chunks)
            
            # 2. Generate answer
            answer = rag_module.generate_answer(user_query)
            
            # 3. Display Answer
            st.subheader("Answer")
            st.success(answer)
            
            # 4. Display Sources
            st.subheader("Sources")
            if retrieved_chunks:
                for i, chunk in enumerate(retrieved_chunks, 1):
                    st.text_area(f"Source {i} (Page {chunk['page_number']})", chunk['text'], height=100)
            else:
                st.info("No relevant sources found.")