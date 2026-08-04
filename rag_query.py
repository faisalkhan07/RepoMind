import os
import chromadb
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Connect to our existing vector database
client_db = chromadb.PersistentClient(path="./chroma_db")
collection = client_db.get_or_create_collection(name="micrograd_code")

# Connect to Groq
client_llm = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def ask_question(question):
    # Step 1: RETRIEVAL - find the most relevant code chunks
    results = collection.query(
        query_texts=[question],
        n_results=3
    )
    
    # Step 2: Build context from retrieved chunks
    context_pieces = []
    for i in range(len(results["documents"][0])):
        code = results["documents"][0][i]
        meta = results["metadatas"][0][i]
        context_pieces.append(
            f"File: {meta['file']}, Line: {meta['line']}, Name: {meta['name']}\n{code}"
        )
    
    context = "\n\n---\n\n".join(context_pieces)
    
    # Step 3: Build the prompt - this is where we combine question + retrieved code
    prompt = f"""You are a helpful assistant that answers questions about a codebase.
Use ONLY the following code snippets to answer the question. If the answer isn't in the snippets, say so.

CODE SNIPPETS:
{context}

QUESTION: {question}

ANSWER:"""

    # Step 4: GENERATION - send to LLM
    response = client_llm.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content


# Test it
question = "How does backpropagation work in this codebase?"
answer = ask_question(question)
print("QUESTION:", question)
print()
print("ANSWER:")
print(answer)