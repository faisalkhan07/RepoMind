# Import the library that turns text into embeddings
from sentence_transformers import SentenceTransformer

# Load a small, free, pre-trained model that knows how to create embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# A few example sentences to compare
sentences = [
    "The cat sat on the mat",
    "A kitten was resting on the rug",
    "The stock market crashed today"
]

# Convert each sentence into an embedding (a list of numbers)
embeddings = model.encode(sentences)

# Print the shape: how many sentences, and how many numbers per sentence
print("Shape:", embeddings.shape)

# Print the first 5 numbers of the first sentence's embedding, just to see what it looks like
print("First 5 numbers of sentence 1:", embeddings[0][:5])

# Import a function that measures how "close" two embeddings are
from sentence_transformers import util

# Compare sentence 1 ("cat on mat") with sentence 2 ("kitten on rug") - should be similar
similarity_1_2 = util.cos_sim(embeddings[0], embeddings[1])
print("Similarity (cat/mat vs kitten/rug):", similarity_1_2)

# Compare sentence 1 ("cat on mat") with sentence 3 ("stock market") - should be different
similarity_1_3 = util.cos_sim(embeddings[0], embeddings[2])
print("Similarity (cat/mat vs stock market):", similarity_1_3)