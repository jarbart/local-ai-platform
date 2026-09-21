# Local AI Platform

Local-first document intelligence platform for ingestion, semantic retrieval and grounded AI conversations.

The project is designed as a portfolio-grade local AI system that combines document processing, vector search and local LLM inference into a single modular platform.

The current implementation provides a working end-to-end RAG pipeline with a Streamlit user interface.

---

## Project status

**Current stage: MVP / Document Platform foundation**

The current system supports:

* PDF document ingestion
* TXT document ingestion
* SHA-256 document identity
* document deduplication
* text chunking with overlap
* semantic embeddings
* vector storage with Qdrant
* semantic similarity search
* retrieval score threshold
* local LLM inference through Ollama
* source attribution
* document listing
* document deletion
* conversational Streamlit UI
* document management UI
* API and integration tests

The project is intentionally being developed incrementally: first a working vertical slice, followed by broader document support, retrieval improvements, evaluation and additional AI capabilities.

---

## Architecture

```text
                         ┌──────────────────────┐
                         │     Streamlit UI      │
                         │                      │
                         │  Documents + Chat    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │                      │
                         │  Upload / Documents  │
                         │  Chat / Health       │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
     ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
     │   Documents   │      │   Retrieval   │      │      LLM      │
     │               │      │               │      │               │
     │ PDF / TXT     │      │ Embeddings    │      │    Ollama     │
     │ Extraction    │      │ Qdrant        │      │ Local model   │
     │ Chunking      │      │ Similarity    │      │               │
     └───────────────┘      │ Threshold     │      └───────────────┘
                            └───────────────┘
```

---

## RAG pipeline

A document follows this processing pipeline:

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
Answer + Sources
```

The system deliberately separates retrieval from generation.

The LLM does not search the documents directly. Relevant document chunks are retrieved first and then passed to the model as context.

A retrieval score threshold is also applied before generation. This allows the system to reject weak matches instead of blindly passing unrelated content to the LLM.

---

## Current UI

The Streamlit interface provides:

* document upload
* document processing
* indexed document list
* document deletion
* conversational chat
* conversation history
* source information
* retrieval relevance indicators

The application is designed to be usable locally without requiring a cloud AI provider.

---

## Supported formats

### Currently supported

| Format | Extraction                   |
| ------ | ---------------------------- |
| PDF    | PyMuPDF                      |
| TXT    | Native UTF-8 text extraction |

### Planned

| Format      | Planned support     |
| ----------- | ------------------- |
| DOCX        | Yes                 |
| HTML        | Yes                 |
| XLSX        | Yes                 |
| JPG         | Yes                 |
| PNG         | Yes                 |
| Scanned PDF | OCR                 |
| Images      | OCR + preprocessing |

---

## Technology stack

### Backend

* Python 3.11
* FastAPI
* Pydantic
* Uvicorn

### Document processing

* PyMuPDF
* custom document normalization
* custom chunking

### Retrieval

* Sentence Transformers
* Qdrant
* cosine similarity

### LLM

* Ollama
* local models such as Llama 3.1

### Frontend

* Streamlit

### Infrastructure

* Docker
* Docker Compose
* Qdrant

### Testing

* pytest
* FastAPI TestClient
* integration tests using real embeddings and Qdrant

---

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
│   ├── test_api.py
│   ├── test_chunking.py
│   ├── test_document_deduplication.py
│   ├── test_document_model.py
│   ├── test_document_service.py
│   ├── test_real_document.py
│   ├── test_real_retrieval.py
│   └── test_retrieval.py
│
├── docs/
│   └── requirements.md
│
├── scripts/
│
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

---

## Requirements

* Windows 11 / Linux
* Python 3.11+
* Git
* Docker Desktop
* Ollama
* local LLM model
* approximately 10+ GB of free disk space for models and dependencies

The project is designed primarily for local development.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/jarbart/local-ai-platform.git
cd local-ai-platform
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Qdrant

Start Qdrant using Docker Compose:

```powershell
docker compose up -d
```

Qdrant will be available at:

```text
http://localhost:6333
```

The project uses a local Qdrant collection for document chunks and embeddings.

---

## Ollama

Install and run Ollama locally.

Example:

```powershell
ollama pull llama3.1:8b
```

Start the Ollama server if it is not already running:

```powershell
ollama serve
```

The default configuration uses:

```text
http://localhost:11434
```

---

## Configuration

The project provides `.env.example`:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Copy it to `.env` if custom configuration is required.

The default configuration is designed to work with the local development environment.

---

## Running the API

Start FastAPI:

```powershell
uvicorn app.api.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

---

## Running the UI

In a second terminal:

```powershell
streamlit run app/ui.py
```

The UI will be available at:

```text
http://localhost:8501
```

---

## API

### Health

```http
GET /health
```

### List documents

```http
GET /documents
```

### Upload document

```http
POST /documents/upload
```

Supported:

* PDF
* TXT

### Delete document

```http
DELETE /documents/{document_id}
```

### Chat

```http
POST /chat
```

Example:

```json
{
  "question": "What is the price of Trek Rail 9?"
}
```

The response contains the generated answer and the document sources used for retrieval.

---

## Example workflow

```text
1. Start Docker
2. Start Ollama
3. Start FastAPI
4. Start Streamlit
5. Upload a PDF or TXT file
6. Document is extracted and chunked
7. Chunks are embedded
8. Embeddings are stored in Qdrant
9. Ask a question
10. Relevant chunks are retrieved
11. Weak retrieval matches are filtered
12. Context is sent to the local LLM
13. Answer and sources are displayed in the UI
```

---

## Testing

Run the complete test suite:

```powershell
pytest
```

The project currently includes unit, API and integration tests covering:

* document models
* PDF extraction
* TXT extraction
* chunking
* page-aware chunking
* document deduplication
* API validation
* document upload
* retrieval
* real embeddings
* Qdrant retrieval
* real document processing

The test suite currently passes with:

```text
15 passed
```

Some dependency-level deprecation warnings may be displayed by FastAPI/Starlette/httpx/anyio. They do not currently originate from application code.

---

## Design principles

### Local-first

The platform is designed to run locally and avoid mandatory cloud AI dependencies.

### Provider agnostic

LLM access is isolated behind a provider layer so additional providers can be introduced later without rewriting the application.

### Evidence-based answers

Answers are generated from retrieved document context and accompanied by source information.

### Deterministic document identity

Documents are identified using SHA-256 content hashes, allowing duplicate uploads to be detected.

### Retrieval before generation

The LLM is not treated as the search engine. Retrieval happens first and only relevant context is passed to the model.

### Defensive RAG

Low-relevance retrieval results are filtered before generation to reduce unsupported answers.

### Testable architecture

Core functionality is separated into document processing, embeddings, retrieval and LLM layers, allowing components to be tested independently.

---

## Current limitations

The current version is intentionally focused on the core RAG workflow.

Known limitations include:

* only PDF and TXT ingestion
* no OCR yet
* basic chunking strategy
* dense semantic retrieval only
* no reranking
* no hybrid BM25/vector retrieval
* no retrieval evaluation dataset
* no authentication
* no multi-user support
* no streaming LLM responses
* no persistent chat history
* limited document metadata
* single local Ollama provider

These are planned improvements rather than accidental omissions.

---

## Roadmap

### Phase 1 — Foundation

* [x] project architecture
* [x] configuration
* [x] FastAPI API
* [x] Docker Compose
* [x] Qdrant integration
* [x] Ollama integration
* [x] testing foundation

### Phase 2 — MVP RAG

* [x] PDF ingestion
* [x] TXT ingestion
* [x] document normalization
* [x] chunking
* [x] embeddings
* [x] semantic retrieval
* [x] score threshold
* [x] grounded LLM answers
* [x] source attribution

### Phase 3 — Document platform

* [x] document listing
* [x] document deletion
* [x] Streamlit UI
* [x] conversational interface
* [x] document management UI
* [ ] DOCX
* [ ] HTML
* [ ] XLSX
* [ ] JPG / PNG
* [ ] OCR
* [ ] richer metadata

### Phase 4 — Retrieval platform

* [ ] hybrid retrieval
* [ ] BM25
* [ ] reranking
* [ ] configurable retrieval parameters
* [ ] retrieval evaluation dataset
* [ ] retrieval metrics
* [ ] context optimization

### Phase 5 — LLM platform

* [ ] provider abstraction improvements
* [ ] model configuration
* [ ] streaming responses
* [ ] generation metrics
* [ ] prompt management
* [ ] model comparison

### Phase 6 — AI applications

* [ ] General Assistant
* [ ] System Analyst
* [ ] structured document extraction
* [ ] document classification
* [ ] future agentic workflows

### Phase 7 — Evaluation & Portfolio

* [ ] benchmark datasets
* [ ] end-to-end evaluation
* [ ] performance measurements
* [ ] example datasets
* [ ] reproducible demo

---

## Goal

The long-term goal is to evolve this project from a simple local RAG application into a modular **local AI platform** capable of supporting multiple document intelligence and AI assistant workloads.

The emphasis is on:

```text
Local-first
    +
Modular architecture
    +
Retrieval quality
    +
Evidence-based generation
    +
Observability
    +
Reproducibility
    +
Testing
    +
Measurable evaluation
```

The project is intentionally built as a modular monolith first. More distributed architecture can be introduced later if real requirements justify it.

---

## Repository

GitHub:

https://github.com/jarbart/local-ai-platform
