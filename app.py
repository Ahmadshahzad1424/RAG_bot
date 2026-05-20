# ========================================
# STREAMLIT RAG CHATBOT INTERFACE
# ========================================
import streamlit as st
from rag_chatbot import RAGChatbot
from pdf_processor import PDFProcessor
from embedding_store import EmbeddingStore
import os
import uuid
from auth import authenticate_user, create_user, update_password, delete_user

# Initialize session state for auth and app
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "full_name" not in st.session_state:
    st.session_state.full_name = None
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

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
    /* Removed hardcoded background-color to fix text visibility in dark mode */
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 RAG Document Q&A System")

if not st.session_state.authenticated:
    st.markdown("Please sign in or sign up to access your personal knowledge base.")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        st.subheader("Sign In")
        login_username = st.text_input("Email Address", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            is_auth, user_full_name = authenticate_user(login_username, login_password)
            if is_auth:
                st.session_state.authenticated = True
                st.session_state.username = login_username
                st.session_state.full_name = user_full_name
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid email or password")
                
    with tab2:
        st.subheader("Sign Up")
        signup_name = st.text_input("Full Name", key="signup_name")
        signup_username = st.text_input("New Email Address (Gmail)", key="signup_username")
        signup_password = st.text_input("New Password", type="password", key="signup_password")
        signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
        if st.button("Register"):
            if not signup_name.strip():
                st.error("Please enter your full name.")
            elif not signup_username.lower().endswith("@gmail.com"):
                st.error("Please use a valid @gmail.com address.")
            elif signup_password != signup_confirm:
                st.error("Passwords do not match!")
            elif len(signup_username) < 13 or len(signup_password) < 6:
                st.error("Invalid email length or password must be at least 6 chars.")
            else:
                success, msg = create_user(signup_username, signup_password, signup_name)
                if success:
                    st.success("Account created successfully! Please sign in.")
                else:
                    st.error(f"Registration failed: {msg}")
                    
    # Stop execution here if not authenticated
    st.stop()

st.markdown(f"Welcome back, **{st.session_state.full_name}**! Upload PDFs to build your personal knowledge base.")

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
    
    # Sanitize username for ChromaDB collection name (only allows a-zA-Z0-9._-)
    sanitized_username = st.session_state.username.replace("@", "_").replace(".", "_")
    user_collection_name = f"user_data_{sanitized_username}"
    
    # Hide the collection name from user since it's now personal
    collection_name = user_collection_name
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chatbot = None
        st.session_state.messages = []
        st.success("✅ Conversation history cleared")
        
    try:
        store = EmbeddingStore(collection_name=collection_name)
        
        # Fetch all existing documents from ChromaDB
        collection_data = store.collection.get(include=["metadatas"])
        if collection_data and collection_data["metadatas"]:
            # Extract unique filenames
            unique_sources = list(set([meta.get("source", "Unknown Document") for meta in collection_data["metadatas"] if meta]))
            
            st.markdown("---")
            st.subheader("📁 Your Documents")
            for source in unique_sources:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"📄 {source}")
                with col_b:
                    # Add a button to delete individual documents
                    if st.button("❌", key=f"del_{source}", help="Remove this document from knowledge base"):
                        # Delete from ChromaDB where source matches
                        store.collection.delete(where={"source": source})
                        st.success(f"Removed {source}")
                        st.session_state.chatbot = None
                        st.session_state.processed_file = None
                        st.rerun()
        
        st.markdown("---")
        if st.button("⚠️ Clear Knowledge Base"):
            store.client.delete_collection(name=collection_name)
            st.session_state.chatbot = None
            st.session_state.processed_file = None
            st.success("✅ Your personal knowledge base has been completely erased.")
            st.rerun()
            
    except Exception as e:
        pass
        
    st.markdown("---")
    
    with st.expander("🔐 Account Settings"):
        st.subheader("Change Password")
        old_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        if st.button("Update Password"):
            if not old_pw or not new_pw:
                st.error("Please fill in both fields.")
            elif len(new_pw) < 6:
                st.error("New password must be at least 6 characters.")
            else:
                success, msg = update_password(st.session_state.username, old_pw, new_pw)
                if success:
                    st.success("Password updated successfully!")
                else:
                    st.error(msg)
                    
        st.markdown("---")
        st.subheader("Danger Zone")
        if st.button("🚨 Delete Account", type="primary"):
            # Clear knowledge base
            try:
                store = EmbeddingStore(collection_name=collection_name)
                store.client.delete_collection(name=collection_name)
            except Exception:
                pass
            
            # Delete user from DB
            delete_user(st.session_state.username)
            
            # Log out
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.full_name = None
            st.session_state.chatbot = None
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.full_name = None
        st.session_state.chatbot = None
        st.session_state.messages = []
        st.rerun()

# Handle file upload
if uploaded_file is not None:
    # Only process if it's a new file
    if st.session_state.processed_file != uploaded_file.name:
        with st.spinner("📖 Processing PDF..."):
            temp_filename = f"temp_{st.session_state.session_id}.pdf"
            
            # Save uploaded file temporarily
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Process PDF
                processor = PDFProcessor(chunk_size=chunk_size, overlap=100)
                chunks = processor.process(temp_filename)
                
                # Store in ChromaDB
                store = EmbeddingStore(collection_name=collection_name)
                
                # Notice we do NOT delete the collection here anymore!
                # This allows users to upload multiple documents into their personal knowledge base.
                metadata_list = [{"source": uploaded_file.name} for _ in range(len(chunks))]
                store.store_chunks(chunks, metadata_list=metadata_list)
                
                # Re-initialize chatbot to make sure it uses the updated collection
                st.session_state.chatbot = RAGChatbot(collection_name=collection_name)
                st.session_state.processed_file = uploaded_file.name
                
                # Show success
                st.success(f"✅ Loaded {uploaded_file.name} with {len(chunks)} chunks!")
                
                # Show stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Chunks", len(chunks))
                with col2:
                    st.metric("Chunk Size", f"{chunk_size} chars")
                with col3:
                    st.metric("Collection", collection_name)
                    
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")
            finally:
                # Clean up temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

# Always initialize the chatbot if it's not None, or if they have a knowledge base
if st.session_state.chatbot is None:
    # Try to load existing knowledge base
    try:
        store = EmbeddingStore(collection_name=collection_name)
        if store.collection.count() > 0:
            st.session_state.chatbot = RAGChatbot(collection_name=collection_name)
    except Exception:
        pass

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
    st.info("👈 **Open the sidebar menu on the left** to upload a PDF file and get started!")