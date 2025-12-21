from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

#embedding_model = get_registry().get("gemini-text").create(name="gemini-embedding-001")

GEMINI_EMBEDDING_DIM = 768

class Chunk(LanceModel):
    chunk_id: str
    filename: str
    text: str
    page_number: int
    vector: Vector(GEMINI_EMBEDDING_DIM)

class Prompt(BaseModel):
    prompt: str = Field(description="prompt form user, if empty consider it as missing")

class Source(BaseModel):
    filename: str = Field(description="filename of retrieved file without suffix")
    page_number: int

class Response(BaseModel):
    sources: list[Source]
    response: str = Field(description="answer based on PDF-document")


