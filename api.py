from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import os
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from github_loader import fetch_repo_files

load_dotenv()
api_key=os.getenv("GROQ_API_KEY")
client=Groq(api_key=api_key)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

class github(BaseModel):
    url:str

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
