from fastapi import FastAPI, HTTPException
from openai import OpenAI  # New OpenAI client (1.x+)
from langchain_community.vectorstores import FAISS  # Local vector DB for similarity search
from langchain_huggingface import HuggingFaceEmbeddings  # To generate text embeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv  # To load environment variables from .env
import os
from fastapi.middleware.cors import CORSMiddleware  # Allows frontend to call this backend
from pydantic import BaseModel  # For request body validation in FastAPI

# Load environment variables (like OPENAI_API_KEY)
load_dotenv()

# Initialize OpenAI client using the API key
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define where the vectorstore is stored
VECTORSTORE_PATH = "./vectorstore"

# Create FastAPI app
app = FastAPI()

# Enable CORS so frontend (on localhost:3001) can call backend (on port 8002)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the FAISS vector store with BGE-Large embeddings
def load_vector_store():
    try:
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en")
        return FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        raise RuntimeError(f"Failed to load vector store: {e}")

# Log loading status
print("Starting to load vector store...")
vector_store = load_vector_store()
print("Vector store loaded successfully!")

# LLM wrapper using OpenAI GPT (3.5)
class CustomLLM:
    def __init__(self):
        pass

    def __call__(self, prompt):
        # Sends the full prompt to GPT-3.5 via chat.completions API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Safebot, the helpful and friendly assistant for University Centre Peterborough."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()

llm = CustomLLM()

# RAG Logic: Retrieves context from vectorstore and combines it with OpenAI answers
class CustomRetrievalQA:
    def __init__(self, llm, retriever, memory_limit=3):
        self.llm = llm
        self.retriever = retriever
        self.memory = []  # Stores past Q&A for short-term memory
        self.memory_limit = memory_limit  # How many past Q&A to remember

    def run(self, query):
        try:
            # Step 1: Semantic search to get relevant chunks
            docs = self.retriever.invoke(query)

            if not docs:
                return "I couldn't find information related to your question."

            # Step 2: Add previous Q&A memory (chat-style)
            if self.memory:
                memory_context = "\n".join(
                    [f"Previous Question: {q}\nPrevious Answer: {a}" for q, a in self.memory[-self.memory_limit:]]
                )
            else:
                memory_context = ""

            # Step 3: Format retrieved documents as context
            document_context = "\n".join([
                f"Source: {doc.metadata.get('source', 'unknown')}\n"
                f"Section: {doc.metadata.get('section', 'General')}\n"
                f"Content: {doc.page_content}"
                for doc in docs
            ])

            # Step 4: Combine everything into one prompt for the LLM
            prompt = f"""
You are Safebot, a helpful, friendly assistant for University Centre Peterborough.

You are currently engaged in a conversation with a student.
Use both the memory of previous conversations and the context below to answer appropriately.
If the answer is not in the context, say "I don't know."

Memory:
{memory_context}

Context:
{document_context}

New Question: {query}

Answer:
"""

            # Step 5: Get the final response from the LLM
            response = self.llm(prompt)

            # Step 6: Save this Q&A pair to memory
            self.memory.append((query, response))

            return response

        except Exception as e:
            print(f"Error in CustomRetrievalQA.run: {e}")
            raise

# Retriever configuration (Semantic Search with MMR)
retriever = vector_store.as_retriever(
    search_type="mmr",  # Maximal Marginal Relevance = diverse + relevant
    search_kwargs={
        "k": 5,            # Final top 5 results
        "fetch_k": 15,     # Consider top 15 before choosing diverse ones
        "lambda_mult": 0.8 # Balance diversity vs similarity
    }
)

# Initialize QA chain
qa_chain = CustomRetrievalQA(llm=llm, retriever=retriever, memory_limit=3)

# === FastAPI ROUTES ===

# GET / => health check / test route
@app.get("/")
def catch_all():
    return {"message": "Labas Egle"}

# Pydantic model for POST body
class QueryRequest(BaseModel):
    query: str

# POST /ask => main chatbot endpoint
@app.post("/ask")
def ask_question(request: QueryRequest):
    query = request.query
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        response = qa_chain.run(query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {e}")

# POST /clear_memory => resets short-term memory
@app.post("/clear_memory")
def clear_memory():
    qa_chain.memory = []
    return {"message": "Memory cleared successfully"}







