from fastapi import FastAPI, HTTPException
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# Load environment variables
load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
VECTORSTORE_PATH = "./vectorstore"

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Load the FAISS vector store
def load_vector_store():
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        raise RuntimeError(f"Failed to load vector store: {e}")

print("Starting to load vector store...")
vector_store = load_vector_store()
print("Vector store loaded successfully!")

# Hugging Face Inference API using InferenceClient
client = InferenceClient(model=MODEL_NAME, token=HUGGINGFACE_TOKEN)

# Custom wrapper using InferenceClient
class CustomLLM:
    def __init__(self, client):
        self.client = client

    def __call__(self, prompt):
        response = self.client.text_generation(
            prompt=prompt,
            max_new_tokens=512,
            temperature=0.5
        )
        return response.strip()

# Initialize the LLM
llm = CustomLLM(client)

# Custom RetrievalQA logic
class CustomRetrievalQA:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.memory = []  # Store conversation history as a list of (question, answer) tuples

    def run(self, query):
        try:
            print(f"Retrieving documents for query: {query}")
            docs = self.retriever.invoke(query)
            print(f"Retrieved documents: {docs}")
            context = "\n".join([doc.page_content for doc in docs])

            # Include memory in the context
            memory_context = "\n".join([f"Q: {q}\nA: {a}" for q, a in self.memory])
            full_context = f"{memory_context}\n\nContext:\n{context}"

            prompt = f"""You are a helpful and friendly University Centre Peterborough assistant, your name is Safebot. Answer the following question based on the context provided.
If the answer is not in the context, say "I don’t know" and do not generate your own questions or guesses, or options. And provide friendly conversation if it is not a question".

{full_context}

Question: {query}
Answer:"""
            response = self.llm(prompt)

            # Add the current question and answer to memory
            self.memory.append((query, response))

            return response
        except Exception as e:
            print(f"Error in CustomRetrievalQA.run: {e}")
            raise

qa_chain = CustomRetrievalQA(llm=llm, retriever=vector_store.as_retriever())

@app.get("/")
def catch_all():
    return {"message": "Labas Egle"}

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask_question(request: QueryRequest):
    query = request.query
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    # Bad language filter
    banned_words = ["fuck", "dick", "dumb", "bitch", "shit", "asshole", "idiot", "boobs", "pussy", "nigger", "slut", "faggot", "retard", "nigga", "whore"]
    lowered_query = query.lower()
    if any(bad_word in lowered_query for bad_word in banned_words):
        return {
            "response": "Let's keep things respectful. I'm here to help with your university questions 😊"
        }
    try:
        response = qa_chain.run(query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {e}")
    
@app.post("/clear_memory")
def clear_memory():
    qa_chain.memory = []  # Clear the memory
    return {"message": "Memory cleared successfully"}






