# 📚 RAG Document Assistant

A retrieval-augmented generation (RAG) chatbot capable of answering questions based on uploaded PDF documents. This project was developed as a diploma thesis (**Examensarbete**) for the Data Engineer program at **Stockholms Tekniska Institut (STI)**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.43%2B-red)
![LanceDB](https://img.shields.io/badge/Vector_DB-LanceDB-orange)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-green)

## 🚀 Features

-   **Interactive Chat Interface:** Modern, Gemini-style chat input with drag-and-drop file support.
-   **RAG Architecture:** Combines vector search (LanceDB) with generative AI (Google Gemini) for accurate, context-aware answers.
-   **Transparent Citations:** Every answer includes exact source references (page numbers and text snippets) to prevent hallucinations.
-   **Local Processing:** PDF ingestion and vectorization happen locally using `pypdf` and `lancedb`.
-   **Efficient Data Handling:** Uses `uv` for fast dependency management.

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend Logic:** Python
* **Vector Database:** LanceDB (Serverless/Embedded)
* **LLM:** Google Gemini (via `google-generativeai`)
* **PDF Parsing:** pypdf
* **Package Manager:** uv

## 📂 Project Structure

```text
rag-doc-bot-examensarbete/
├── backend/
│   ├── data_models.py    # Data classes (Chunk) and schema definitions
│   ├── ingestion.py      # Logic for PDF parsing and vector database insertion
│   ├── rag.py            # RAG pipeline: Retrieval + Generation
│   └── retrieval.py      # Search logic for LanceDB
├── data/
│   ├── lancedb/          # Local vector database files (auto-generated)
│   └── raw/              # Stored PDF files
├── frontend/
│   └── app.py            # Main Streamlit application
├── explorations/         # Jupyter notebooks for prototyping
├── .env                  # Environment variables (API keys)
├── .python-version       # Python version lock
├── pyproject.toml        # Project dependencies
└── README.md             # Project documentation
```

⚙️ Installation & Setup
This project uses uv for extremely fast package management.

1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/rag-doc-bot-examensarbete.git](https://github.com/YOUR_USERNAME/rag-doc-bot-examensarbete.git)
cd rag-doc-bot-examensarbete
```

2. Set up environment variables
Create a .env file in the root directory and add your Google Gemini API key:
```Ini, TOML
GOOGLE_API_KEY=your_google_api_key_here
```

3. Install dependencies
```bash
uv sync
```


▶️ Usage
Run the application using uv:
```bash
uv run streamlit run frontend/app.py
```

Open your browser at the provided URL (usually http://localhost:8501).

Upload a PDF: Click the paperclip icon 📎 in the chat bar or drag a file into the input area.

Wait for Ingestion: The bot will process the file and save it to the local vector database.

Chat: Ask questions about the document. View sources in the expandable "View sources" section under each answer.