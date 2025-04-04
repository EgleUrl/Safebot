# Description: This script processes the documents in the chatbot-docs folder and creates a vector store for the chatbot.
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Path to the chatbot-docs folder
DOCS_PATH = "./chatbot-docs"  

# Hugging Face embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def process_documents():
    # Load all .md files from the chatbot-docs folder
    documents = []
    for filename in os.listdir(DOCS_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(DOCS_PATH, filename)
            loader = TextLoader(filepath, encoding="utf-8")
            documents.extend(loader.load())

    # Split documents into smaller chunks for better embedding
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # Create embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Create a FAISS vector store
    vector_store = FAISS.from_documents(docs, embeddings)

    # Save the vector store to disk
    vector_store.save_local("vectorstore")
    print("Vector store created and saved!")

if __name__ == "__main__":
    process_documents()