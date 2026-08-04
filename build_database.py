import ast
import os
import chromadb

def extract_chunks_from_file(filepath):
    """Read a Python file and extract function/class chunks using AST."""
    with open(filepath, "r", encoding="utf-8") as f:
        source_code = f.read()
    
    if not source_code.strip():
        return []
    
    tree = ast.parse(source_code)
    
    chunks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            code_chunk = ast.get_source_segment(source_code, node)
            chunks.append({
                "name": node.name,
                "type": "class" if isinstance(node, ast.ClassDef) else "function",
                "code": code_chunk,
                "file": filepath,
                "line": node.lineno
            })
    
    return chunks


def extract_chunks_from_repo(repo_path):
    """Walk through every .py file in a repo and collect all chunks."""
    all_chunks = []
    for root, dirs, files in os.walk(repo_path):
        for filename in files:
            if filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                chunks = extract_chunks_from_file(filepath)
                all_chunks.extend(chunks)
    return all_chunks


# Step 1: Get our chunks (same as before)
all_chunks = extract_chunks_from_repo("micrograd")
print(f"Extracted {len(all_chunks)} chunks")

# Step 2: Create a ChromaDB client (this stores data on disk in a folder)
client = chromadb.PersistentClient(path="./chroma_db")

# Step 3: Create (or get) a "collection" — think of it like a table in a database
collection = client.get_or_create_collection(name="micrograd_code")

# Step 4: Add all our chunks into the collection
# ChromaDB needs: documents (the actual text), ids (unique names), and metadatas (extra info)
documents = []
ids = []
metadatas = []

for i, chunk in enumerate(all_chunks):
    documents.append(chunk["code"])
    ids.append(f"chunk_{i}")  # simple unique ID like "chunk_0", "chunk_1", etc.
    metadatas.append({
        "name": chunk["name"],
        "type": chunk["type"],
        "file": chunk["file"],
        "line": chunk["line"]
    })

collection.add(
    documents=documents,
    ids=ids,
    metadatas=metadatas
)

print(f"Stored {collection.count()} chunks in ChromaDB")