import streamlit as st
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

import backend.rag as rag_module

st.title("RAG Document Bot (MVP)")

user_query = st.text_input("Ask your question here:")

if st.button("Send"):
    if user_query:
        with st.spinner("Generating answer..."):
            answer = rag_module.generate_answer(user_query)
            st.write("### Answer:")
            st.write(answer)
    else:
        st.warning("Please enter a question first.")