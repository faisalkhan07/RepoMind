import ast
import os
import subprocess
import chromadb
from sentence_transformers import SentenceTransformer

# Load our code-specialized embedding model once, reused across calls
embedding_model = SentenceTransformer("flax-sentence-embeddings/st-codesearch-distilroberta-base")


def extract_chunks_from_file(filepath):
    """Read a Python file and extract function/class chunks using AST, with parent-class context."""
    with open(filepath, "r", encoding="utf-8") as f:
        source_code = f.read()

    if not source_code.strip():
        return []

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []

    chunks = []

    # Walk the tree, but track which class (if any) we're currently inside
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            code_chunk = ast.get_source_segment(source_code, node)

            # Find the parent class name, if this node is a method
            parent_class = None
            for potential_parent in ast.walk(tree):
                if isinstance(potential_parent, ast.ClassDef):
                    for child in ast.iter_child_nodes(potential_parent):
                        if child is node:
                            parent_class = potential_parent.name

            docstring = ast.get_docstring(node) or ""

            chunks.append({
                "name": node.name,
                "type": "class" if isinstance(node, ast.ClassDef) else "function",
                "code": code_chunk,
                "file": filepath,
                "line": node.lineno,
                "parent_class": parent_class,
                "docstring": docstring
            })

    return chunks


def build_embedding_text(chunk):
    """Build a richer text representation of a chunk for embedding (more context = better search)."""
    parts = []

    if chunk["parent_class"]:
        parts.append(f"Class: {chunk['parent_class']}")

    parts.append(f"File: {os.path.basename(chunk['file'])}")
    parts.append(f"{chunk['type'].capitalize()}: {chunk['name']}")

    if chunk["docstring"]:
        parts.append(f"Docstring: {chunk['docstring']}")

    parts.append(chunk["code"])

    return "\n".join(parts)


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


def repo_name_from_url(repo_url):
    name = repo_url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def clone_repo(repo_url, base_path="./repos"):
    os.makedirs(base_path, exist_ok=True)
    repo_name = repo_name_from_url(repo_url)
    local_path = os.path.join(base_path, repo_name)

    if not os.path.exists(local_path):
        subprocess.run(["git", "clone", repo_url, local_path], check=True)

    return local_path, repo_name


def ingest_repo(repo_url):
    """Full ingestion: clone, chunk, embed (with our own model), and store in ChromaDB."""
    local_path, repo_name = clone_repo(repo_url)
    chunks = extract_chunks_from_repo(local_path)

    client = chromadb.PersistentClient(path="./chroma_db")
    collection_name = f"repo_{repo_name}"
    collection = client.get_or_create_collection(name=collection_name)

    documents = []
    ids = []
    metadatas = []
    embedding_texts = []

    for i, chunk in enumerate(chunks):
        documents.append(chunk["code"])
        ids.append(f"chunk_{i}")
        metadatas.append({
            "name": chunk["name"],
            "type": chunk["type"],
            "file": chunk["file"],
            "line": chunk["line"],
            "parent_class": chunk["parent_class"] or ""
        })
        embedding_texts.append(build_embedding_text(chunk))

    if documents:
        # Generate embeddings ourselves using our chosen model
        embeddings = embedding_model.encode(embedding_texts).tolist()

        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
            embeddings=embeddings
        )

    return {
        "repo_name": repo_name,
        "collection_name": collection_name,
        "chunks_stored": len(documents)
    }