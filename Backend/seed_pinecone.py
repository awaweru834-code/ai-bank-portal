import os
from pypdf import PdfReader
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environmental variables from .env
load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")

# 1. Initialize Pinecone and Embedding Model
print("Initializing cloud connections...")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Use the local model (outputs 384 dimensions)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Read the PDF
print("Reading handbook.pdf...")
reader = PdfReader("handbook.pdf")

documents = []
ids = []

# 3. Extract text page-by-page
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text and text.strip():
        documents.append(text)
        ids.append(f"page_{i+1}")

print(f"Extracted {len(documents)} valid pages.")

# 4. Generate Embeddings & Upload to Pinecone
print("Translating pages into cloud math coordinates...")

vectors_to_upsert = []
for doc_id, doc_text in zip(ids, documents):
    # Convert text chunk into a list of floats
    embedding = embedding_model.encode(doc_text).tolist()
    
    # Print dimension of the first vector just to double-check
    if len(vectors_to_upsert) == 0:
        print(f"ℹ️ Your local vectors have exactly {len(embedding)} dimensions.")

    # Using explicit dictionary format for maximum compatibility with the new SDK
    vectors_to_upsert.append({
        "id": doc_id,
        "values": embedding,
        "metadata": {"text": doc_text}
    })

print("Uploading to Pinecone cloud index...")
# Upload to Pinecone using named argument format
index.upsert(vectors=vectors_to_upsert)

print("\n✅ Cloud Database successfully built! Your PDF is now safely stored in Pinecone.")