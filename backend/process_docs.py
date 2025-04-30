# Description: This script processes Markdown documents in the chatbot-docs folder
# and creates a FAISS vector store for semantic search in a chatbot (RAG system).

import os
from langchain_community.document_loaders import TextLoader  # For loading text files (.md)
from langchain_community.vectorstores import FAISS  # FAISS = Fast similarity search (local vector DB)
from langchain_huggingface import HuggingFaceEmbeddings  # HuggingFace embedding model wrapper
from langchain.text_splitter import RecursiveCharacterTextSplitter  # For splitting text into chunks

# Path to the folder containing your university knowledge base (.md files)
DOCS_PATH = "./chatbot-docs"

# Choose your embedding model (here: BGE-Large = strong semantic embeddings)
EMBEDDING_MODEL = "BAAI/bge-large-en"

def process_documents():
    documents = []

    # Step 1: Load all Markdown files from the chatbot-docs folder
    for filename in os.listdir(DOCS_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(DOCS_PATH, filename)
            loader = TextLoader(filepath, encoding="utf-8")
            documents.extend(loader.load())  # Each .md becomes a Document object

    # Step 2: Split long documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,        # Max 500 characters per chunk
        chunk_overlap=50       # 50-character overlap for continuity
    )
    docs = text_splitter.split_documents(documents)

    # Step 3: Convert chunks into vector embeddings using BGE-Large
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Step 4: Create a FAISS vector index for fast semantic search
    vector_store = FAISS.from_documents(docs, embeddings)

    # Step 5: Save the vector store to local disk (to be loaded by app.py)
    vector_store.save_local("vectorstore")

    print(" Vector store created and saved!")

# Entry point: if you run this script directly python process.py, it will process and store embeddings
if __name__ == "__main__":
    process_documents()
