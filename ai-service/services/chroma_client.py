import chromadb
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create DB client
client = chromadb.Client()
collection = client.create_collection("docs")

# Add documents
def add_docs(texts):
    embeddings = model.encode(texts).tolist()
    ids = [str(i) for i in range(len(texts))]
    collection.add(documents=texts, embeddings=embeddings, ids=ids)

# THIS IS IMPORTANT FUNCTION
def query_docs(query):
    q_embed = model.encode([query]).tolist()
    results = collection.query(query_embeddings=q_embed, n_results=3)
    return results
    # add sample data (run once)
sample_data = [
    "Cyber attacks can cause data breaches and system failures",
    "Financial risks include market loss and revenue decline",
    "Operational risks affect business processes and delays",
    "Technical risks include server downtime and software bugs"
]

add_docs(sample_data)