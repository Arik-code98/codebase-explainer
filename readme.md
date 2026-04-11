## Codebase Explainer

Codebase Explainer is a backend service that lets you ask questions about any public GitHub repository using natural language. It fetches the code, builds a vector index over it, and then uses an LLM to answer questions grounded in the repository’s files.

> 🚧 Note: The frontend for this project is currently under construction.

---

### Features
- Index any public GitHub repository by URL.
- Store embeddings persistently using ChromaDB.
- Ask natural-language questions about the indexed codebase.
- Get answers along with referenced source file paths.

---

### Tech Stack
- FastAPI (backend API)
- LangChain (document & chunk management)
- HuggingFace Embeddings (`all-MiniLM-L6-v2`)
- ChromaDB (vector store)
- Groq (LLM API)
- PyGithub (GitHub integration)

---

### API Overview

Base URL: `http://localhost:8000`

- `GET /`  
	Health check. Returns a simple JSON message confirming the API is running.

- `POST /index`  
	Indexes a GitHub repository.
	- Request body:
		```json
		{
			"url": "https://github.com/owner/repo"
		}
		```
	- Response:
		```json
		{
			"repo_id": "<generated_id>"
		}
		```

- `POST /ask`  
	Asks a question about a previously indexed repository.
	- Request body:
		```json
		{
			"repo_id": "<generated_id>",
			"question": "Explain how authentication works"
		}
		```
	- Response (shape simplified):
		```json
		{
			"sources": ["path/to/file1.py", "path/to/file2.py"],
			"answer": "...model-generated explanation..."
		}
		```

---

### Getting Started

#### 1. Clone the repository

```bash
git clone https://github.com/Arik-code98/codebase-explainer
cd codebase-explainer
```

#### 2. Create and activate a virtual environment (optional but recommended)

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set environment variables

Create a `.env` file in the project root with:

```env
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_token
```

#### 5. Run the API server

```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`. You can also use the auto-generated docs at `http://localhost:8000/docs`.
