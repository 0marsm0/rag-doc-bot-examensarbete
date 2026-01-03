import os
import google.generativeai as genai
from dotenv import load_dotenv
from retrieval import search_db

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
load_dotenv(os.path.join(project_root, '.env'))

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"

def generate_answer(query: str, history: list = []):
    print(f"Thinking ...")

    retrieved_chunks = search_db(query, limit=3)

    if not retrieved_chunks:
        return {
            "answer": "I could't find information in the document.",
            "sources": []
        }
    
    context_text = ""
    for chunk in retrieved_chunks:
        context_text += f"\nPage {chunk['page_number']}:\n{chunk['text']}"

    chat_history_text = ""
    for msg in history:
        role = "User" if msg['role'] == "user" else "AI"
        content = msg['content']
        chat_history_text += f"{role}: {content}\n"

    prompt = f"""
        You are a helpful AI assistant.
        Your task is to answer the user's question based ONLY on the provided context excerpts from a PDF document.
        
        CONTEXT FROM DOCUMENT:
        {context_text}

        CHAT HISTORY (Previous conversation):
        {chat_history_text}

        INSTRUCTIONS:
        1. Answer the question using the provided context.
        2. If the question is general (e.g., "What is this document about?"), analyze the snippets to infer the general topic (e.g., look for course names, program structures, or headers).
        3. Use the CHAT HISTORY to understand context (e.g. if user says "it", look at previous messages).
        4. You can draw logical conclusions, but do not hallucinate facts not present in the text.
        5. If the answer is completely missing, state that you don't know based on the provided text.
        
        Question: {query}
        
        Answer:
    """

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    
    
    return {
        "answer": response.text,
        "sources": retrieved_chunks
    }

if __name__ == "__main__":
    #test_question = "Vad handlar detta dokument om?"
    test_question = "Vilka förkunskapskrav gäller?"
    
    print("Generating the answer...")
    answer = generate_answer(test_question)
    
    print("ANSWER FROM GEMINI:")
    print(answer)
