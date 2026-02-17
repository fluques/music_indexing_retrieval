import faiss
import os
from music_indexing_retrieval import settings
from pathlib import Path
index=None

def load_or_create_faiss_index():
    global index 
    if os.path.exists(settings.FAISS_INDEX_PATH):
        print(f"Loading FAISS index from {settings.FAISS_INDEX_PATH}")
        try:
            index= faiss.read_index(settings.FAISS_INDEX_PATH)
            return index
        except Exception as e:
            print(f"Error loading index: {e}")

    # If the index doesn't exist, create it (e.g., from database embeddings)
    dim = 12
    M=32
    ef_construction=200
    index = faiss.IndexFlatL2(dim)
    #index = faiss.IndexHNSWFlat(dim, M)
    #index.hnsw.efConstruction = ef_construction
    if not os.path.exists(os.path.dirname(settings.FAISS_INDEX_PATH)):
        os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH))
    faiss.write_index(index, settings.FAISS_INDEX_PATH)

    return index

def get_faiss_index():
    global index 
    if index is None:
        return load_or_create_faiss_index()
    return index


