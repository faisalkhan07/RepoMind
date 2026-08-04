import os
import chromadb
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()

client_db = chromadb.PersistentClient(path="./chroma_db")
client_llm = Groq(api_key=os.environ.get("GROQ_API_KEY"))
embedding_model = SentenceTransformer("flax-sentence-embeddings/st-codesearch-distilroberta-base")


def retrieve_chunks(question, collection_name, n_results=3):
    collection = client_db.get_or_create_collection(name=collection_name)

    query_embedding = embedding_model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "code": results["documents"][0][i],
            "file": results["metadatas"][0][i]["file"],
            "line": results["metadatas"][0][i]["line"],
            "name": results["metadatas"][0][i]["name"],
            "type": results["metadatas"][0][i]["type"],
            "distance": results["distances"][0][i]
        })

    return retrieved


def build_prompt(question, chunks):
    context_pieces = []
    for i, chunk in enumerate(chunks):
        citation_label = f"[{i+1}]"
        context_pieces.append(
            f"{citation_label} File: {chunk['file']}, Line: {chunk['line']}, Name: {chunk['name']} ({chunk['type']})\n{chunk['code']}"
        )

    context = "\n\n".join(context_pieces)

    prompt = f"""You are a helpful assistant that answers questions about a codebase.
Use ONLY the following code snippets to answer. Reference snippets using their citation numbers like [1], [2], etc. when you use information from them.
If the answer isn't in the snippets, say so clearly.

CODE SNIPPETS:
{context}

QUESTION: {question}

ANSWER (include citation numbers like [1] where relevant):"""

    return prompt


def ask_question(question, collection_name, n_results=3):
    chunks = retrieve_chunks(question, collection_name, n_results)

    if not chunks:
        return {
            "answer": "I couldn't find any relevant code for this question. Try ingesting the repo first, or rephrase your question.",
            "sources": []
        }

    prompt = build_prompt(question, chunks)

    response = client_llm.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": chunks
    }