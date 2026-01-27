import faiss
import os
import numpy as np

VECTOR_DIM = 384
INDEX_PATH = "vector_store/faiss.index"

class VectorStore:
    def __init__(self):
        self.index = faiss.IndexFlatIP(VECTOR_DIM)

    def add(self, vector: list[float]):
        vec = np.array([vector]).astype("float32")
        faiss.normalize_L2(vec)
        self.index.add(vec)

    def save(self):
        os.makedirs("vector_store", exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)

    def load(self):
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)

vector_store = VectorStore()
