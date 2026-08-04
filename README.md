# RepoMind

Ask questions about any GitHub codebase in plain English and get grounded, cited answers — powered by Retrieval-Augmented Generation (RAG).

## What it does

RepoMind lets you point it at any public GitHub repository, and then ask natural language questions about the code. Instead of hallucinating answers, it retrieves the actual relevant functions/classes from the codebase and grounds its response in real, cited source code (file + line number).

## How it works

1. **Ingestion** — clones a repo and parses every Python file using the `ast` module, extracting functions and classes as individual chunks (not naive character-based splitting)
2. **Embedding** — each chunk is embedded using `flax-sentence-embeddings/st-codesearch-distilroberta-base`, a model fine-tuned specifically for code search, with added context (parent class, docstring, file name) to improve retrieval quality
3. **Storage** — chunks are stored in ChromaDB, with each repo isolated in its own collection
4. **Retrieval** — a user's question is embedded with the same model and matched against stored chunks using semantic similarity
5. **Generation** — the top matching chunks are passed to an LLM (Groq, Llama 3.1) with explicit instructions to answer only from the provided context and cite sources

## Tech stack

- **Backend:** FastAPI, Python
- **Embeddings:** sentence-transformers (CodeSearch-DistilRoBERTa)
- **Vector database:** ChromaDB
- **LLM:** Groq (Llama 3.1 8B Instant)
- **Code parsing:** Python `ast` module

## API endpoints

- `POST /ingest` — clone and index a GitHub repo (`{"repo_url": "..."}`)
- `POST /ask` — ask a question about an ingested repo (`{"question": "...", "collection_name": "...", "n_results": 3}`)

## Engineering notes

Retrieval quality was iteratively improved by:
- Adding AST-based parent-class and docstring context to each chunk before embedding
- Switching from a general-purpose embedding model (`all-MiniLM-L6-v2`) to a code-specialized one (`CodeSearch-DistilRoBERTa`)

On test queries against the micrograd codebase, this reduced average match distance (lower = more similar) from ~1.27–1.31 to ~1.17–1.21 — roughly a 7-8% improvement — and noticeably reduced hedging/uncertainty in generated answers, with the LLM providing more complete, confident explanations grounded in the retrieved code.

## Setup

1. Clone this repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it and install dependencies: `pip install -r requirements.txt`
4. Add a `.env` file with your `GROQ_API_KEY`
5. Run the server: `uvicorn main:app --reload`
6. Visit `http://127.0.0.1:8000/docs` to try it out

## Status

Backend complete. Web UI in progress.