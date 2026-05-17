# ========================================
# PART 1: IMPORTS
# ========================================
from chromadb import PersistentClient
import os

class EmbeddingStore:
    """
    This class does ONE job: Store chunks as embeddings in ChromaDB
    
    ChromaDB = vector database that:
    - Takes text chunks
    - Converts them to embeddings (fingerprints)
    - Stores them so we can search later
    """
    
    def __init__(self, collection_name="rag_documents"):
        """
        Setup ChromaDB with persistence (data survives between runs)
        """
        # Create data directory if it doesn't exist
        os.makedirs("./chroma_data", exist_ok=True)
        
        # Use persistent client (saves to disk)
        self.client = PersistentClient(path="./chroma_data")
        
        # Get or create a collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.collection_name = collection_name
    
    def store_chunks(self, chunks, metadata_list=None):
        """
        JOB: Take text chunks and store them in ChromaDB
        """
        if metadata_list is None:
            metadata_list = [{"source": "document", "chunk_id": i} for i in range(len(chunks))]
        
        self.collection.add(
            ids=[f"chunk_{i}" for i in range(len(chunks))],
            documents=chunks,
            metadatas=metadata_list
        )
        
        print(f"✅ Stored {len(chunks)} chunks in collection '{self.collection_name}'")
    
    def search(self, query, num_results=3):
        """
        JOB: Find relevant chunks based on user's question
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=num_results
        )
        
        return results
    
    def get_stats(self):
        """
        JOB: Show how many chunks we have stored
        """
        count = self.collection.count()
        return {
            "collection": self.collection_name,
            "total_chunks": count
        }


# ========================================
# PART 2: TEST IT
# ========================================
if __name__ == "__main__":
    from pdf_processor import PDFProcessor
    
    print("Step 1: Processing PDF...\n")
    processor = PDFProcessor(chunk_size=500, overlap=100)
    chunks = processor.process("sample.pdf")
    
    print("\nStep 2: Storing chunks in ChromaDB...\n")
    store = EmbeddingStore(collection_name="rl_documents")
    store.store_chunks(chunks)
    
    print("\nStep 3: Stats...\n")
    stats = store.get_stats()
    print(f"Collection: {stats['collection']}")
    print(f"Total chunks: {stats['total_chunks']}")
    
    print("\nStep 4: Testing search...\n")
    query = "What is a multi-armed bandit?"
    print(f"Query: {query}\n")
    
    results = store.search(query, num_results=2)
    
    for i, (chunk_id, document, distance) in enumerate(
        zip(results["ids"][0], results["documents"][0], results["distances"][0])
    ):
        print(f"--- Result {i+1} (similarity: {1 - distance:.2%}) ---")
        print(document[:200] + "...\n")