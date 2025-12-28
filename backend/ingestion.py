import os
import lancedb
from typing import List
from pypdf import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
from data_models import Chunk


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
dotenv_path = os.path.join(project_root, '.env')
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

DB_PATH = os.path.join(project_root, "data", "lancedb")
TABLE_NAME = "pdf_knowledge_base"

os.makedirs(DB_PATH, exist_ok=True)

def get_pdf_text(filepath: str) -> List[dict]:
    try:
        reader = PdfReader(filepath)
        chunks = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                chunks.append({'page': i, 'content': text})
        return chunks
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    response = genai.embed_content(
        model="models/text-embedding-004", 
        content=texts, 
        task_type="retrieval_document"
    )
    return response["embedding"]


def ingestion(file_path: str):
    print(f"Start ingestion for {file_path}")
    
    # 1. Reading PDF
    print("Reading PDF...")
    chunks_data = get_pdf_text(file_path)
    
    if not chunks_data:
        print("No text extracted from PDF.")
        return False

    raw_texts = [chunk['content'] for chunk in chunks_data]

    # 2. Generating vectors
    print(f"Generating embeddings for {len(raw_texts)} pages...")
    try:
        vectors = generate_embeddings(raw_texts)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return False

    # 3. Preparing data
    filename = os.path.basename(file_path)
    data_to_insert = []
    
    for chunk_data, vector in zip(chunks_data, vectors):
        chunk = Chunk(
            chunk_id=f"{filename}_{chunk_data['page']}", 
            filename=filename,
            text=chunk_data['content'],
            page_number=chunk_data['page'],
            vector=vector
        )
        data_to_insert.append(chunk)

    # 4. Writing chunks to LanceDB
    print(f"Writing {len(data_to_insert)} chunks to LanceDB at {DB_PATH}")
    try:
        vector_db = lancedb.connect(uri=DB_PATH)
        
        vector_db.create_table(
            TABLE_NAME, 
            schema=Chunk, 
            mode="overwrite", 
            data=data_to_insert
        )
        print("Ingestion complete!")
        return True
        
    except Exception as e:
        print(f"Error saving to LanceDB: {e}")
        return False

if __name__ == "__main__":
    # Test file from data/raw
    test_pdf = os.path.join(project_root, "data", "raw", "EGSYS.pdf")
    if os.path.exists(test_pdf):
        ingestion(test_pdf)
    else:
        print(f"File not found: {test_pdf}")