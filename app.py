# ========================================
# STREAMLIT RAG CHATBOT INTERFACE
# ========================================
import streamlit as st
from rag_chatbot import RAGChatbot
from pdf_processor import PDFProcessor
from embedding_store import EmbeddingStore
import os
import uuid
from auth import authenticate_user, create_user, update_password, delete_user, create_session, get_user_from_session, clear_session
from streamlit_cookies_controller import CookieController

# Page config (must be the first Streamlit command)
st.set_page_config(
    page_title="📚 RAG Document Q&A",
    page_icon="🤖",
    layout="wide"
)

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
if "db_session_token" not in st.session_state:
    st.session_state.db_session_token = None

# Initialize Cookie Controller
controller = CookieController()

# ---- Persistent Login Check ----
# Check if a session token exists in browser cookies
session_token = controller.get("session_token")

if not st.session_state.authenticated and session_token:
    user_data = get_user_from_session(session_token)
    if user_data:
        st.session_state.authenticated = True
        st.session_state.username = user_data["username"]
        st.session_state.full_name = user_data["full_name"]
        st.session_state.db_session_token = session_token
    else:
        # Invalid or expired token
        controller.remove("session_token")

# Enterprise CSS for better styling
st.markdown("""
    <style>
    /* Hide default Streamlit elements for a cleaner SaaS look */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container width */
    .block-container {
        padding-top: 1rem;
        max-width: 1000px;
    }
    
    /* Modern inputs */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 2px rgba(37,99,235,0.2);
    }
    
    /* Enterprise Buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid rgba(128,128,128,0.2);
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-color: rgba(128,128,128,0.3);
    }
    
    /* Primary buttons (like login/register) */
    button[kind="primary"] {
        background-color: #ff9900;
        color: white;
        border: none;
    }
    button[kind="primary"]:hover {
        background-color: #e68a00;
    }
    
    /* Chat bubbles */
    .stChatMessage {
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(128,128,128,0.15);
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Premium Custom Header Banner (AWS Style)
st.markdown("""
<div style="background: linear-gradient(90deg, #232f3e 0%, #1a222d 100%); padding: 2rem 2.5rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-bottom: 4px solid #ff9900;">
    <h1 style="color: white; margin: 0; font-size: 2.2rem; font-weight: 700; font-family: 'Segoe UI', Roboto, sans-serif; letter-spacing: -0.5px;">Enterprise Document Intelligence</h1>
    <p style="color: #94a3b8; margin-top: 0.5rem; margin-bottom: 0; font-size: 1.05rem;">Secure Retrieval-Augmented Generation Architecture</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_auth, _ = st.columns([1, 2, 1])
    
    with col_auth:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #232f3e; font-weight: 700;'>Welcome to DocuBrain AI</h2>
            <p style='color: #64748b;'>Sign in to access your secure knowledge base.</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Sign In", "✨ Create Account"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            # Sanitize input to prevent trailing space bugs
            login_username = st.text_input("Email Address", key="login_username").strip().lower()
            login_password = st.text_input("Password", type="password", key="login_password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Secure Login", use_container_width=True, type="primary"):
                is_auth, user_full_name = authenticate_user(login_username, login_password)
                if is_auth:
                    st.session_state.authenticated = True
                    st.session_state.username = login_username
                    st.session_state.full_name = user_full_name
                    
                    # Create persistent session and set Cookie
                    token = create_session(login_username)
                    st.session_state.db_session_token = token
                    controller.set("session_token", token, max_age=86400 * 30) # 30 days
                    
                    st.rerun()
                else:
                    st.error("Invalid email or password")
                    
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            signup_name = st.text_input("Full Name", key="signup_name").strip()
            # Sanitize registration email
            signup_username = st.text_input("Work Email Address (Gmail)", key="signup_username").strip().lower()
            signup_password = st.text_input("New Password", type="password", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register Account", use_container_width=True, type="primary"):
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

st.markdown(f"Welcome back, **{str(st.session_state.full_name).strip()}**! Upload PDFs to build your personal knowledge base.")

# Sidebar for controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Sanitize username for ChromaDB collection name (only allows a-zA-Z0-9._-)
    sanitized_username = st.session_state.username.replace("@", "_").replace(".", "_")
    collection_name = f"user_data_{sanitized_username}"
    
    # 1. Fetch existing documents to enforce quota
    current_doc_count = 0
    unique_sources = []
    try:
        store = EmbeddingStore(collection_name=collection_name)
        collection_data = store.collection.get(include=["metadatas"])
        if collection_data and collection_data["metadatas"]:
            unique_sources = list(set([meta.get("source", "Unknown Document") for meta in collection_data["metadatas"] if meta]))
            current_doc_count = len(unique_sources)
    except Exception:
        pass

    # 2. Display Quota Usage
    st.markdown(f"**Storage Quota:** {current_doc_count} / 5 Documents")
    st.progress(current_doc_count / 5.0)
    
    # 3. File uploader (disabled if quota reached)
    if current_doc_count >= 5:
        st.warning("⚠️ Free tier limit reached. Please delete an existing document below to upload more.")
        uploaded_file = None
    else:
        uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])
    
    with st.expander("⚙️ Advanced Engine Settings"):
        st.caption("Developer parameters for the RAG Engine.")
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
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chatbot = None
        st.session_state.messages = []
        st.success("✅ Conversation history cleared")
        
    try:
        if unique_sources:
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
            
            # Clear session
            if st.session_state.db_session_token:
                clear_session(st.session_state.db_session_token)
            controller.remove("session_token")
            
            # Log out
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.full_name = None
            st.session_state.db_session_token = None
            st.session_state.chatbot = None
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout"):
        if st.session_state.db_session_token:
            clear_session(st.session_state.db_session_token)
        controller.remove("session_token")
            
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.full_name = None
        st.session_state.db_session_token = None
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
                st.success(f"✅ Successfully added **{uploaded_file.name}** to your knowledge base!")
                    
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
    
    # Display chat history or empty state
    if not st.session_state.messages:
        st.markdown("""
        <div style='text-align: center; margin-top: 4rem; margin-bottom: 4rem;'>
            <h1 style='font-size: 2.5rem; color: #1e293b; font-weight: 700;'>How can I help you today?</h1>
            <p style='color: #64748b; font-size: 1.1rem;'>Ask a question, request a summary, or extract data from your secure knowledge base.</p>
            <p style='color: #94a3b8; font-size: 0.95rem; margin-top: 1.5rem;'>
                <em>💡 Want to add or remove files? Open the <strong>⚙️ Settings</strong> menu in the left sidebar.</em>
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
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