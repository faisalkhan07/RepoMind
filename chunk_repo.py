import ast
import os

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


# Run it on the whole micrograd repo
all_chunks = extract_chunks_from_repo("micrograd")

print(f"Total chunks found across the repo: {len(all_chunks)}")
print()

# Print a quick summary: just name, type, file for each chunk (no full code, too much text)
for chunk in all_chunks:
    print(f"[{chunk['type']}] {chunk['name']} — {chunk['file']} (line {chunk['line']})")