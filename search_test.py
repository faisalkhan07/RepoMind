import chromadb

# Connect to the same database we just built
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="micrograd_code")

# Ask a question in plain English
query = "how does backpropagation work"

# Search for the most similar chunks
results = collection.query(
    query_texts=[query],
    n_results=3  # get the top 3 most relevant chunks
)

# Print the results
for i in range(len(results["documents"][0])):
    print("=" * 50)
    print("Match", i + 1)
    print("File:", results["metadatas"][0][i]["file"])
    print("Name:", results["metadatas"][0][i]["name"])
    print("Line:", results["metadatas"][0][i]["line"])
    print("Distance (lower = more similar):", results["distances"][0][i])
    print()
    print(results["documents"][0][i][:200])  # first 200 chars of the code