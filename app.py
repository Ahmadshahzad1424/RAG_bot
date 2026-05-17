# ========================================
# STREAMLIT RAG CHATBOT INTERFACE
# ========================================
import streamlit as st
from rag_chatbot import RAGChatbot
from pdf_processor import PDFProcessor
from embedding_store import EmbeddingStore
import os

# Page config
st.set_page_config(
    page_title="📚 RAG Document Q&A",
    page_icon="🤖",
    layout="wide"
)

# CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 RAG Document Q&A System")
st.markdown("Upload a PDF and ask questions about its content")

# Sidebar for controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # File uploader
    uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])
    
    chunk_size = st.slider(
        "Chunk Size",
        min_value=300,
        max_value=1000,
        value=500,
        step=100,
        help="Number of characters per chunk"
    )
    
    num_chunks = st.slider(
        "Relevant Chunks",
        min_value=1,
        max_value=10,
        value=3,
        help="How many chunks to retrieve for context"
    )
    
    collection_name = st.text_input(
        "Collection Name",
        value="rag_documents",
        help="Name of the ChromaDB collection"
    )
    
    if st.button("🗑️ Clear History"):
        st.session_state.chatbot = None
        st.success("✅ Conversation history cleared")

# Initialize session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Handle file upload
if uploaded_file is not None:
    with st.spinner("📖 Processing PDF..."):
        # Save uploaded file temporarily
        with open("temp_pdf.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Process PDF
        processor = PDFProcessor(chunk_size=chunk_size, overlap=100)
        chunks = processor.process("temp_pdf.pdf")
        
        # Store in ChromaDB
        store = EmbeddingStore(collection_name=collection_name)
        store.store_chunks(chunks)
        
        # Create chatbot
        st.session_state.chatbot = RAGChatbot(collection_name=collection_name)
        
        # Show success
        st.success(f"✅ Loaded PDF with {len(chunks)} chunks!")
        
        # Show stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Chunks", len(chunks))
        with col2:
            st.metric("Chunk Size", f"{chunk_size} chars")
        with col3:
            st.metric("Collection", collection_name)

# Main chat interface
if st.session_state.chatbot is not None:
    st.divider()
    
    # Display chat history
    st.subheader("💬 Conversation")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input area
    question = st.chat_input(
        "Ask a question about the document...",
        key="user_input"
    )
    
    if question:
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(question)
        
        # Get answer from chatbot
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                answer = st.session_state.chatbot.query(question, num_chunks=num_chunks)
            st.markdown(answer)
        
        # Add assistant message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })
else:
    st.info("👆 Upload a PDF file to get started!")