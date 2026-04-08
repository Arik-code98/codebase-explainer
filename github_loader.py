# github_loader.py
from github import Github, Auth
from langchain_core.documents import Document
import os

def fetch_repo_files(repo_url: str) -> list[Document]:
    token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(token)
    g = Github(auth=auth)
    
    repo_name = repo_url.replace("https://github.com/", "")
    repo = g.get_repo(repo_name)
    
    tree = repo.get_git_tree(sha="main", recursive=True)
    
    code_extensions = ['.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml']
    documents = []
    
    for item in tree.tree:
        if any(item.path.endswith(ext) for ext in code_extensions):
            file_content = repo.get_contents(item.path)
            content = file_content.decoded_content.decode("utf-8")
            documents.append(Document(
                page_content=content,
                metadata={"source": item.path}
            ))
    
    return documents