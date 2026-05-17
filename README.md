# 🤖 RAG Document Q&A System

A robust Retrieval-Augmented Generation (RAG) chatbot application that allows users to upload PDF documents and ask questions about their content. Built with **Streamlit**, **Groq**, and **ChromaDB**.

## ✨ Features

- **📄 PDF Processing:** Upload any PDF document and automatically extract its text. The text is chunked with customizable sizes and overlaps.
- **🧠 Vector Database:** Uses **ChromaDB** to locally store embeddings and retrieve the most relevant document chunks based on user queries.
- **⚡ High-Speed LLM:** Powered by **Groq**'s ultra-fast API, using state-of-the-art models (like Llama-3.3-70b) to generate context-aware answers.
- **💬 Conversational Memory:** The chatbot remembers the history of your current session, allowing for follow-up questions.
- **🎨 Interactive UI:** A clean, easy-to-use web interface built with **Streamlit**.

## 🛠️ Architecture

- `app.py`: The main Streamlit web application. Handles the UI, file uploads, and chat interface.
- `rag_chatbot.py`: The core RAG logic. Connects to Groq, retrieves context from ChromaDB, and generates the final answer.
- `embedding_store.py`: Manages the ChromaDB vector database (storing and searching chunks).
- `pdf_processor.py`: Handles reading the PDF files and splitting the text into chunks.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- A [Groq API Key](https://console.groq.com/keys)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ahmadshahzad1424/RAG_bot.git
   cd RAG_bot
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

### Running the App

Run the Streamlit application with the following command:

```bash
streamlit run app.py
```

The app will open automatically in your browser (usually at `http://localhost:8501`).

## 💡 How to Use
1. Open the app in your browser.
2. Upload a PDF document using the sidebar.
3. Wait for the app to process the PDF and store it in the vector database.
4. Start asking questions in the chat input! You can clear the history or adjust chunk settings from the sidebar.
