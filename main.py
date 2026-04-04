from dotenv import load_dotenv
import os
from github import Github, Auth

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

auth = Auth.Token(TOKEN)
g = Github(auth=auth)

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

print(f"Total files fetched: {len(documents)}")