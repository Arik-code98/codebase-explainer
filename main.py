from dotenv import load_dotenv
import os
from github import Github, Auth
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

auth = Auth.Token(TOKEN)
g = Github(auth=auth)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

repo_url = "https://github.com/Arik-code98/rag-api"
repo_name = repo_url.replace("https://github.com/", "")
repo = g.get_repo(repo_name)

tree = repo.get_git_tree(sha="main", recursive=True)
code_extensions = ['.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml']

documents = []

for item in tree.tree:
    if any(item.path.endswith(ext) for ext in code_extensions):
        file_content = repo.get_contents(item.path)
        content = file_content.decoded_content.decode("utf-8")
        documents.append({
            "path": item.path,
            "content": content
        })

# Convert to LangChain Document format
langchain_docs = []
for doc in documents:
    langchain_docs.append(Document(
        page_content=doc["content"],
        metadata={"source": doc["path"]}
    ))

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(langchain_docs)

vector_store = Chroma(
    collection_name="codebase",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

vector_store.add_documents(chunks)
