from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import os
import uuid
from fastapi import HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from chromadb import PersistentClient
from github_loader import fetch_repo_files

load_dotenv()
api_key=os.getenv("GROQ_API_KEY")
client=Groq(api_key=api_key)
chroma_client = PersistentClient(path="./chroma_db")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

class github(BaseModel):
    url:str

class qna(BaseModel):
    repo_id:str
    question:str

app=FastAPI()

@app.get("/")
def root():
    return{'Message':"api is running"}

@app.post("/index")
def index_repo(link: github):
    repo_id = uuid.uuid4().hex
    docs = fetch_repo_files(link.url)
    chunks = text_splitter.split_documents(docs)
    vector_store = Chroma(
        collection_name=repo_id,
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
    vector_store.add_documents(chunks)
    return {"repo_id": repo_id}

@app.post("/ask")
def chat(ai:qna):
    repo_id = ai.repo_id
    try:
        chroma_client.get_collection(name=repo_id)
    except Exception:
        raise HTTPException(status_code=404, detail="doc not found")
    
    vector_store = Chroma(
        collection_name=repo_id,
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    docs = vector_store.similarity_search(ai.question, k=4)
    context = "\n\n".join(doc.page_content for doc in docs)

    sources = []
    seen_sources = set()
    for doc in docs:
        source = doc.metadata.get("source")
        if source and source not in seen_sources:
            seen_sources.add(source)
            sources.append(source)

    prompt = f"""You are a helpful assistant that answers questions about a codebase.

    Context:
    {context}

    Question:
    {ai.question}
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )

    return {"sources": sources, "answer": response.choices[0].message.content}
