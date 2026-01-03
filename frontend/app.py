import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

current_dir = Path(__file__).parent
project_root = current_dir.parent
backend_path = project_root / "backend"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

import backend.rag as rag_module
import backend.ingestion as ingestion_module

# Page configuration
st.set_page_config(
    page_title="RAG Document Bot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }
    
    .source-box {
        background-color: #f0f2f6;
        border-left: 3px solid #4CAF50;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        font-size: 0.9em;
    }
    
    .stButton>button {
        border-radius: 20px;
        padding: 8px 16px;
        white-space: nowrap; 
        text-overflow: ellipsis; 
        overflow: hidden;
        width: 100%;
        font-size: 0.9rem;
    }
    
    div[data-testid="stChatInput"] {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 20px 0;
        z-index: 100;
    }
    
    .timestamp {
        color: #888;
        font-size: 0.8em;
        margin-top: 5px;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    
    section[data-testid="stSidebar"] h1 {
        margin-top: 0 !important;
        font-size: 1.8rem !important;
        padding-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] h2 {
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.2rem !important;
        padding-top: 0 !important;
    }
    section[data-testid="stSidebar"] h3 {
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.0rem !important;
        padding-top: 0 !important;
    }
    
    section[data-testid="stSidebar"] hr {
        margin-top: 1em !important;
        margin-bottom: 1em !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'num_chunks' not in st.session_state:
    st.session_state.num_chunks = 3

# Sidebar
with st.sidebar:
    st.markdown("## 📚 RAG Document Bot")
        
    st.markdown("## ⚙️ Settings")
    st.session_state.num_chunks = st.slider(
        "Context chunks",
        min_value=1,
        max_value=5,
        value=st.session_state.num_chunks,
        help="Number of relevant text sections to retrieve"
    )
    
    show_sources = st.checkbox("Show sources automatically", value=True)
    
    st.markdown("---")
    
    st.markdown("### 💡 Suggested Questions")
    
    if st.button("📋 Summarize", help="Get a quick overview", use_container_width=True):
        st.session_state.suggested_query = "Provide a concise summary of the document with 3-5 key bullet points."
    
    if st.button("📑 Structure", help="List chapters and sections", use_container_width=True):
        st.session_state.suggested_query = "List the main chapters, sections, or topics covered in this document."
    
    if st.button("🛠️ Requirements", help="Tools, equipment, or prerequisites needed", use_container_width=True):
        st.session_state.suggested_query = "What tools, equipment, or prerequisites are required?"
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About the System")
    st.info(
        "This is a RAG bot using:\n\n"
        "🔍 **LanceDB** - Vector Search\n\n"
        "🤖 **Gemini** - AI Generation\n\n"
        "📄 **PyPDF** - Document Reading"
    )
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "<small>v0.1.0</small>"
        "</div>",
        unsafe_allow_html=True
    )

# Main content
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# Display welcome message if chat is empty
if not st.session_state.chat_history:
    st.markdown("""
    <div style='text-align: center; padding: 50px 20px;'>
        <h1>👋 Welcome to RAG Document Bot!</h1>
        <p style='font-size: 1.2em; color: #666;'>
            Ask me questions about your document and I'll help you find answers.
        </p>
        <p style='color: #888;'>
            💡 Try one of the suggested questions in the sidebar
        </p>
    </div>
    """, unsafe_allow_html=True)

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"])
        
        # Display timestamp
        if "timestamp" in message:
            st.markdown(
                f"<div class='timestamp'>{message['timestamp']}</div>",
                unsafe_allow_html=True
            )
        
        # Display sources if they exist
        if "sources" in message and message["sources"]:
            with st.expander(f"📄 View {len(message['sources'])} sources"):
                for i, source in enumerate(message['sources'], 1):
                    st.markdown(
                        f"<div class='source-box'>"
                        f"<strong>Source {i} - Page {source['page_number']}</strong><br>"
                        f"{source['text'][:300]}..."
                        f"</div>",
                        unsafe_allow_html=True
                    )

# Chat input with file upload support
prompt = st.chat_input("Type your question here...", accept_file=True, file_type=["pdf"])

user_input = None
uploaded_files = []

# Handle suggested query from sidebar
if 'suggested_query' in st.session_state:
    user_input = st.session_state.suggested_query
    del st.session_state.suggested_query
elif prompt:
    user_input = prompt.text
    uploaded_files = prompt.files

# Process input
if user_input or uploaded_files:
    
    # Handle file uploads
    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_folder = project_root / "data" / "raw"
            save_path = save_folder / uploaded_file.name
            
            # Ensure folder exists
            save_folder.mkdir(parents=True, exist_ok=True)
            
            with st.spinner(f"Processing {uploaded_file.name}..."):
                # Save file
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Ingest file
                if ingestion_module:
                    success = ingestion_module.ingestion(str(save_path))
                    if success:
                        st.session_state.chat_history = []
                        st.success(f"File '{uploaded_file.name}' processed successfully!")
                    else:
                        st.error(f"Failed to process '{uploaded_file.name}'")
                else:
                    st.error("Ingestion module not found.")

    # Handle text query
    if user_input:
        # Add user message
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "avatar": "👤",
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
            st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)
        
        # Display assistant "thinking"
        with st.chat_message("assistant", avatar="🤖"):
            sources_placeholder = st.empty()
            with st.spinner("Searching document..."):
                try:
                    result = rag_module.generate_answer(
                        user_input, 
                        history=st.session_state.chat_history[-6:-1]
                    )
                    
                    stream_generator = result["stream"]
                    retrieved_chunks = result["sources"]
                    
                    full_response = st.write_stream(stream_generator)

                    timestamp = datetime.now().strftime("%H:%M")
                    st.markdown(f"<div class='timestamp'>{timestamp}</div>", unsafe_allow_html=True)
                    
                    # Prepare sources data
                    sources_data = []
                    if retrieved_chunks:
                        sources_data = [
                            {
                                "page_number": chunk['page_number'],
                                "text": chunk['text']
                            }
                            for chunk in retrieved_chunks
                        ]
                        
                        if show_sources:
                            with st.expander(f"📄 View {len(sources_data)} sources"):
                                for i, source in enumerate(sources_data, 1):
                                    st.markdown(
                                        f"<div class='source-box'>"
                                        f"<strong>Source {i} - Page {source['page_number']}</strong><br>"
                                        f"{source['text'][:300]}..."
                                        f"</div>",
                                        unsafe_allow_html=True
                                    )
                    
                    # Add assistant response to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": full_response, # <-- берем результат st.write_stream
                        "avatar": "🤖",
                        "timestamp": timestamp,
                        "sources": sources_data
                    })
                    
                except Exception as e:
                    error_msg = f"An error occurred: {str(e)}"
                    st.error(error_msg)

st.markdown("</div>", unsafe_allow_html=True)