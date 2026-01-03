import os
import lancedb
import google.generativeai as genai
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

DB_PATH = os.path.join(project_root, "data", "lancedb")
TABLE_NAME = "pdf_knowledge_base"

def search_db(query: str, limit: int = 3, filename: str = None):
    #print(f"\nQuestion: '{query}'")
    #print(f"Searching in database: {DB_PATH}")

    # Connection to the existing database
    if not os.path.exists(DB_PATH):
        print("Error: Couldn't find database! Run ingestion.py first")
        return

    db = lancedb.connect(DB_PATH)

    try:
        tbl = db.open_table(TABLE_NAME)
    except FileNotFoundError:
        print(f"ERROR: Table {TABLE_NAME} not found")
        return []

    # Convert the query into a vector
    response = genai.embed_content(
        model="models/text-embedding-004",
        content=query,
        task_type="retrieval_query" # helps gemini to understand that it is a searching request
    )
    query_vector = response['embedding']

    search_job = tbl.search(query_vector).limit(limit)

    if filename and filename != "All Documents":
        search_job = search_job.where(f"filename = '{filename}'")
        print(f"Searching in: {filename}")
    
    results = search_job.to_list()

    print(f"Found {len(results)} chunks.")
    return results

if __name__ == "__main__":
    # Test query
    search_db("Vilka förkunskapskrav gäller?")