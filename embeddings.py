from sentence_transformers import SentenceTransformer

# Load the model once, shared across the whole app
embedding_model = SentenceTransformer("flax-sentence-embeddings/st-codesearch-distilroberta-base")