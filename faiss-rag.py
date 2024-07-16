# Install required libraries
# Uncomment and run the following lines if you haven't installed these libraries
# !pip install torch transformers faiss-cpu

import os
import numpy as np
import faiss
from transformers import AutoTokenizer, AutoModel
import torch

# Load pre-trained tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


# Function to get vector representation of a document
def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()
    return embeddings


# Directory containing text files
docs_folder = "path_to_your_text_files"

# List to store document vectors
doc_vectors = []
file_names = []

# Read text files and convert to vectors
for file_name in os.listdir(docs_folder):
    file_path = os.path.join(docs_folder, file_name)
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
        vector = get_embedding(text)
        doc_vectors.append(vector)
        file_names.append(file_name)

# Convert list to NumPy array
doc_vectors = np.vstack(doc_vectors)

# Dimension of the vectors
d = doc_vectors.shape[1]

# Create a FlatL2 index
index = faiss.IndexFlatL2(d)

# Add document vectors to the index
index.add(doc_vectors)


# Function to search Faiss index
def search_faiss(query, k=5):
    # Get the vector for the query
    query_vector = get_embedding(query)

    # Perform the search
    distances, indices = index.search(query_vector, k)

    # Retrieve and print the results
    results = []
    for i in range(k):
        results.append((file_names[indices[0, i]], distances[0, i]))
    return results


# Example query
query = "Example query text"
results = search_faiss(query)

print("Results:")
for file_name, distance in results:
    print(f"File: {file_name}, Distance: {distance}")
