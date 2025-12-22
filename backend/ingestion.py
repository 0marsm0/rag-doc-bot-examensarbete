import os
import lancedb
from typing import List
from pypdf import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
from backend.data_models import Chunk, GEMINI_EMBEDDING_DIM

load_dotenv()

DB_PATH = "data/lancedb"
TABLE_NAME = "pdf_knowledge_base"

def get_pdf_text(filepath: str) -> List[dict]:
    reader = PdfReader(filepath)
    chunks = [{'page': i, 'content': page.extract_text()} for i, page in enumerate(reader.pages)]
    return chunks


def generate_embeddings(text_chunks: List[str]) -> List[List[float]]:
    texts = [chunk['content'] for chunk in text_chunks]
    response = genai.embed_content(model="models/text-embedding-004", content=texts)

    return response["embedding"]


def ingestion(file_path: str):
    vector_db = lancedb.connect(uri=DB_PATH)

if __name__ == "__main__":
    ingestion("../data/raw/EGSYS.pgf")