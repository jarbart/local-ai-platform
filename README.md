# Local AI Platform

Local-first document intelligence platform for document ingestion, semantic retrieval and grounded AI conversations.

The project combines document processing, vector search and local LLM inference into a modular monolith with a FastAPI backend and Streamlit UI.

## Project status

**Portfolio-ready MVP / Document Platform foundation**

The current implementation provides a complete local RAG workflow:

* PDF ingestion
* TXT ingestion
* DOCX ingestion
* SHA-256 document identity
* duplicate document detection
* text chunking with overlap
* semantic embeddings
* Qdrant vector storage
* semantic retrieval
* configurable retrieval score threshold
* local LLM inference through Ollama
* grounded answers based on retrieved context
* source attribution
* retrieved-content evidence
* document listing and deletion
* Streamlit document management UI
* conversational chat UI
* API and integration tests

## Architecture

```text
                         ┌──────────────────────┐
                         │     Streamlit UI     │
                         │                      │
                         │ Documents + Chat     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │                      │
                         │ Upload / Documents   │
                         │ Chat / Health        │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
       │   Documents   │     │   Retrieval   │     │      LLM      │
       │               │     │               │     │               │
       │ PDF / TXT     │     │ Embeddings    │     │    Ollama     │
       │ DOCX          │     │ Qdrant        │     │ Local model   │
       │ Extraction    │     │ Similarity    │     │               │
       │ Chunking      │     │ Threshold     │     │               │
       └───────────────┘     └───────────────┘     └───────────────┘
```

The application is intentionally implemented as a **modular monolith**. The internal modules separate API, document processing, embeddings, retrieval and LLM integration without introducing unnecessary distributed infrastructure.

## RAG pipeline

```text
Document
   │
   ▼
Extraction
   │
   ▼
NormalizedDocument
   │
   ▼
Chunking
   │
   ▼
Embeddings
   │
   ▼
Qdrant
   │
   ▼
Semantic Retrieval
   │
   ▼
Score Threshold
   │
   ▼
Relevant Context
   │
   ▼
Ollama
   │
   ▼
Answer + Sources + Evidence
```

Retrieval and generation are deliberately separated.

The LLM does not search the documents directly. Relevant chunks are retrieved first, filtered by a configurable score threshold and then passed to the model as context.

## Supported formats

| Format      | Current support                  |
| ----------- | -------------------------------- |
| PDF         | PyMuPDF extraction               |
| TXT         | UTF-8 text extraction            |
| DOCX        | python-docx paragraph extraction |
| HTML        | Planned                          |
| XLSX        | Planned                          |
| JPG / PNG   | Planned                          |
| Scanned PDF | OCR planned                      |

DOCX extraction currently focuses on document paragraphs. Table extraction is not yet implemented.

## Technology stack

### Backend

* Python 3.11
* FastAPI
* Pydantic
* Uvicorn

### Document processing

* PyMuPDF
* python-docx
* custom document normalization
* custom chunking

### Retrieval

* Sentence Transformers
* Qdrant
* cosine similarity
* configurable score threshold

### LLM

* Ollama
* Llama 3.1 8B by default

### Frontend

* Streamlit

### Infrastructure

* Docker
* Docker Compose
* Qdrant

### Testing

* pytest
* FastAPI TestClient
* real embeddings
* real Qdrant integration tests
* document processing tests

## Project structure

```text
local-ai-platform/
│
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   ├── documents.py
│   │   ├── main.py
│   │   └── models.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── dependencies.py
│   │
│   ├── documents/
│   │   ├── chunking.py
│   │   ├── models.py
│   │   └── service.py
│   │
│   ├── embeddings/
│   │   └── service.py
│   │
│   ├── llm/
│   │   └── ollama.py
│   │
│   ├── retrieval/
│   │   ├── context.py
│   │   └── service.py
│   │
│   └── ui.py
│
├── tests/
├── docs/
├── scripts/
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

* Windows 11 or Linux
* Python 3.11+
* Git
* Docker Desktop
* Ollama
* local LLM model
* approximately 10+ GB of free disk space for models and dependencies

The application is designed primarily for local development.

## Installation

Clone the repository:

```bash
git clone https://github.com/jarbart/local-ai-platform.git
cd local-ai-platform
```

Create a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Qdrant

Start Qdrant:

```powershell
docker compose up -d
```

Qdrant will be available at:

```text
http://localhost:6333
```

## Ollama

Install Ollama and pull the default model:

```powershell
ollama pull llama3.1:8b
```

Start the Ollama server:

```powershell
ollama serve
```

The default endpoint is:

```text
http://localhost:11434
```

## Configuration

Optional configuration can be provided through `.env`.

Start from:

```powershell
Copy-Item .env.example .env
```

Default configuration:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

RAG_SCORE_THRESHOLD=0.25
```

The `.env` file is ignored by Git.

## Running the application

### FastAPI

```powershell
uvicorn app.api.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

### Streamlit

In a second terminal:

```powershell
streamlit run app/ui.py
```

UI:

```text
http://localhost:8501
```

## Example workflow

1. Start Docker / Qdrant.
2. Start Ollama.
3. Start FastAPI.
4. Start Streamlit.
5. Upload a PDF, TXT or DOCX document.
6. The document is extracted and normalized.
7. Text is split into chunks.
8. Chunks are converted into embeddings.
9. Embeddings are stored in Qdrant.
10. Ask a question in the UI.
11. Relevant chunks are retrieved.
12. Low-relevance matches are filtered.
13. Retrieved context is sent to the local LLM.
14. The UI displays the answer, source information and retrieved evidence.

## API

### Health

```text
GET /health
```

### List documents

```text
GET /documents
```

### Upload document

```text
POST /documents/upload
```

Supported:

* PDF
* TXT
* DOCX

### Delete document

```text
DELETE /documents/{document_id}
```

### Chat

```text
POST /chat
```

Example:

```json
{
  "question": "What is the price of Trek Rail 9?"
}
```

The response contains the generated answer and the document sources used for retrieval.

## Testing

Run the complete test suite:

```powershell
pytest -q
```

Current test suite:

**19 passed, 2 dependency warnings**

Coverage includes:

* document models
* PDF extraction
* TXT extraction
* DOCX extraction
* chunking
* page-aware chunking
* document deduplication
* API validation
* document upload
* document deletion
* retrieval
* score threshold behavior
* real embeddings
* Qdrant retrieval
* real document processing
* API response contracts

The two warnings are dependency-level deprecation warnings from the FastAPI/Starlette/httpx/anyio stack and do not currently originate from application code.

## Design principles

### Local-first

The platform runs locally without requiring a mandatory cloud AI provider.

### Provider isolation

LLM access is isolated behind a provider layer so additional providers can be introduced later without rewriting the application.

### Evidence-based answers

Answers are generated from retrieved document context and accompanied by source information and retrieved content.

### Deterministic document identity

Documents are identified using SHA-256 content hashes, allowing duplicate uploads to be detected.

### Retrieval before generation

Retrieval happens before generation. The LLM is not used as the document search engine.

### Defensive RAG

Low-relevance retrieval results are filtered before generation to reduce unsupported answers.

### Testable architecture

Document processing, embeddings, retrieval and LLM integration are separated into dedicated modules and tested independently.

## Current limitations

This version intentionally focuses on the core local RAG workflow.

Known limitations:

* DOCX tables are not extracted
* no OCR
* basic chunking strategy
* dense semantic retrieval only
* no reranking
* no hybrid BM25/vector retrieval
* no retrieval evaluation dataset
* limited document metadata
* no authentication
* no multi-user support
* no streaming LLM responses
* no persistent chat history
* single local Ollama provider

These are deliberate scope limitations of the current portfolio version.

## Future directions

Potential extensions include:

* HTML ingestion
* XLSX ingestion
* image ingestion
* OCR
* richer document metadata
* hybrid BM25/vector retrieval
* reranking
* retrieval evaluation datasets
* retrieval metrics
* context optimization
* additional LLM providers
* streaming responses
* generation metrics
* prompt management
* structured document extraction
* document classification
* agentic workflows

## Goal

The long-term idea behind the project is to explore how a local-first AI platform can combine document processing, retrieval and LLM applications while remaining modular, observable, reproducible and testable.

The current repository intentionally stops at a usable portfolio-grade RAG application rather than attempting to implement every planned capability.

## Repository

GitHub:

https://github.com/jarbart/local-ai-platform
