import os
import lancedb
from typing import List
from pypdf import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
from data_models import Chunk, GEMINI_EMBEDDING_DIM


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
dotenv_path = os.path.join(project_root, '.env')
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

DB_PATH = os.path.join(project_root, "data", "lancedb")
TABLE_NAME = "pdf_knowledge_base"

def get_pdf_text(filepath: str) -> List[dict]:
    reader = PdfReader(filepath)
    chunks = [{'page': i, 'content': page.extract_text()} for i, page in enumerate(reader.pages, start=1)]
    return chunks


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    #texts = [chunk['content'] for chunk in text_chunks]
    response = genai.embed_content(model="models/text-embedding-004", content=texts, task_type="retrieval_document")

    return response["embedding"]


def ingestion(file_path: str):
    #1 
    print(f"--- Start ingestion for {file_path} ---")
    vector_db = lancedb.connect(uri=DB_PATH)

    #2
    print("Reading PDF...")
    chunks_data = get_pdf_text(file_path)
    raw_texts = [chunk['content'] for chunk in chunks_data]

    #3
    print(f"Generating embeddings for {len(raw_texts)} pages...")
    vectors = generate_embeddings(raw_texts)

    #4
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

    #5
    print("Writing to LanceDB...")
    vector_db.create_table(TABLE_NAME, schema=Chunk, mode="overwrite", data=data_to_insert)
    print("--- Ingestion Complete! ---")



if __name__ == "__main__":
    pdf_path = os.path.join(project_root, "data", "raw", "EGSYS.pdf")
    ingestion(pdf_path)