import os
import chromadb
from chromadb.utils import embedding_functions

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="defendx_chunks",
            embedding_function=self.embedding_fn
        )

    def add_chunks(self, chunks):
        """
        chunks: list of dicts with id, text, metadata
        """
        if not chunks:
            return
            
        ids = [str(c["id"]) for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        
        # We use upsert to avoid duplicate IDs crashing the ingestion
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query: str, top_k: int = 5, where=None):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where # example: {"force": "Indian Navy"}
        )
        
        formatted_results = []
        if not results["ids"] or not results["ids"][0]:
            return formatted_results
            
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results and results["distances"] else None
            })
            
        return formatted_results

vector_store = VectorStore()

def get_vector_store():
    return vector_store
