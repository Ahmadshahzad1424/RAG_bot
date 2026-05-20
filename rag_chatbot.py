# ========================================
# PART 1: IMPORTS
# ========================================
from groq import Groq
from embedding_store import EmbeddingStore
from pdf_processor import PDFProcessor
from dotenv import load_dotenv
import os

# Load .env file (where we stored GROQ_API_KEY)
load_dotenv()

class RAGChatbot:
    """
    This class does ONE job: Answer user questions using RAG
    
    RAG = Retrieval Augmented Generation
    - Retrieval = find relevant chunks from ChromaDB
    - Augmented = add those chunks as context
    - Generation = Groq generates answer based on context
    """
    
    def __init__(self, collection_name="rag_documents"):
        """
        Setup everything we need:
        1. ChromaDB (to search chunks)
        2. Groq (to generate answers)
        3. Conversation history (to remember context)
        """
        
        # Get Groq API key from .env file
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY not found in .env file!")
        
        # Create Groq client
        self.groq_client = Groq(api_key=api_key)
        
        # Create embedding store (to search)
        self.store = EmbeddingStore(collection_name=collection_name)
        
        # Store conversation history
        # Why? So Groq remembers previous questions
        self.conversation_history = []
    
    def query(self, question, num_chunks=3):
        """
        JOB: Answer user's question using RAG
        
        INPUT:
        - question = what user is asking
        - num_chunks = how many relevant chunks to use (3 is usually good)
        
        OUTPUT:
        - Answer from Groq
        
        WHAT HAPPENS:
        1. Search ChromaDB for relevant chunks
        2. Format chunks as context
        3. Send question + context to Groq
        4. Groq generates answer
        5. Return answer to user
        """
        
        print(f"\n🔍 Searching for relevant chunks...")
        
        # Step 1: Search ChromaDB
        search_results = self.store.search(question, num_results=num_chunks)
        
        # Step 2: Extract chunks and format them
        if not search_results["documents"] or not search_results["documents"][0]:
            print("⚠️ No relevant chunks found.")
            return "I couldn't find any relevant information in the uploaded document to answer your question."
            
        retrieved_chunks = search_results["documents"][0]
        retrieved_distances = search_results["distances"][0]
        retrieved_metadatas = search_results.get("metadatas", [[{}] * len(retrieved_chunks)])[0]
        
        # Create context string (all chunks together)
        context = "\n\n".join(
            f"[Source Document: {meta.get('source', 'Unknown Document')}]\n{chunk}"
            for chunk, meta, dist in zip(retrieved_chunks, retrieved_metadatas, retrieved_distances)
        )
        
        print(f"✅ Found {len(retrieved_chunks)} relevant chunks")
        
        # Step 3: Create the message for Groq
        # This tells Groq: "Here's context. Use it to answer the question."
        system_message = """You are a highly intelligent, professional AI assistant. 
        
Your task is to answer the user's question by synthesizing the information found in the provided document context.
Follow these rules strictly:
1. Provide a direct, synthesized, and well-written answer. Do NOT just copy-paste bullet points from the text.
2. Sound like a human expert. Do NOT use robotic phrasing like "According to the document it is stated that...".
3. Do NOT use technical jargon like "chunks" or "excerpts".
4. At the very end of your answer, include a subtle citation in italics. Example: *(Source: document_name.pdf)*
5. If the answer is not in the context, simply say "I don't have information about this in the uploaded documents." """
        
        user_message = f"""Context from documents:
{context}

---

Question: {question}

Please answer based on the context above."""
        
        # Add to conversation history
        # This helps Groq remember the context
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Limit conversation history to the last 5 interactions (10 messages: 5 user, 5 assistant)
        # to prevent exceeding the model's context window.
        recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        
        print(f"\n📡 Sending to Groq...\n")
        
        # Step 4: Call Groq API
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Modern, powerful model
                messages=[
                    {"role": "system", "content": system_message},
                    *recent_history  # Only include recent messages
                ],
                temperature=0.7,  # Balance between creative and factual
                max_tokens=1000  # Max length of answer
            )
            
            # Step 5: Extract answer
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"❌ Error communicating with the AI model: {str(e)}"
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": answer
        })
        
        return answer
    
    def clear_history(self):
        """
        JOB: Clear conversation history
        (Start fresh conversation)
        """
        self.conversation_history = []
        print("✅ Conversation history cleared")


# ========================================
# PART 2: TEST IT
# ========================================
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 RAG CHATBOT - GROQ + CHROMADB")
    print("=" * 60)
    
    # Create chatbot
    chatbot = RAGChatbot(collection_name="rl_documents")
    
    # Ask questions
    questions = [
        "What is a multi-armed bandit?",
        "What are the types of bandit problems?",
        "Explain the exploration-exploitation tradeoff"
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"❓ Question: {question}")
        print(f"{'='*60}")
        
        answer = chatbot.query(question)
        print(f"\n✅ Answer:\n{answer}")
        print()