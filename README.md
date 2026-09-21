# Local AI Platform

Local-first platform for building and experimenting with document-based AI applications using open-source models and self-hosted infrastructure.

The project is designed as a **modular monolith** that can gradually evolve from a simple RAG pipeline into a broader local AI platform for document processing, retrieval, LLM integration and AI-assisted applications.

## Project Status

**Current milestone: MVP — working end-to-end RAG pipeline**

The current implementation supports:

* PDF document upload
* PDF text extraction with PyMuPDF
* document identity based on SHA-256
* duplicate document detection
* text chunking with overlap
* vector embeddings with Sentence Transformers
* vector storage and similarity search with Qdrant
* local LLM inference through Ollama
* context construction from retrieved document chunks
* source metadata returned with generated answers
* REST API built with FastAPI
* automated unit and integration tests

The complete flow has been verified locally on Windows 11.

---

## Architecture

The current system follows a modular monolith architecture:

```text
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │                      │
                         │  /health             │
                         │  /documents/upload   │
                         │  /chat               │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 │                                     │
                 ▼                                     ▼
        ┌─────────────────┐                  ┌─────────────────┐
        │ Document        │                  │ Chat            │
        │ Processing      │                  │ Pipeline        │
        └────────┬────────┘                  └────────┬────────┘
                 │                                    │
                 ▼                                    ▼
        ┌─────────────────┐                  ┌─────────────────┐
        │ Text Chunking   │                  │ Retrieval       │
        └────────┬────────┘                  └────────┬────────┘
                 │                                    │
                 ▼                                    ▼
        ┌─────────────────┐                  ┌─────────────────┐
        │ Embeddings      │◄─────────────────│ Qdrant         │
        │ Sentence        │                  │ Vector Store    │
        │ Transformers    │                  └────────┬────────┘
        └────────┬────────┘                           │
                 │                                    ▼
                 └──────────────────────────► ┌─────────────────┐
                                              │ Context Builder │
                                              └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │ Ollama          │
                                              │ Local LLM       │
                                              └─────────────────┘
```

The architecture intentionally keeps infrastructure concerns behind application services so that retrieval, embedding and LLM components can be extended without redesigning the entire application.

---

## RAG Pipeline

The current end-to-end pipeline is:

```text
PDF
 │
 ▼
Document extraction
 │
 ▼
Normalized document
 │
 ▼
Text chunking
 │
 ▼
Embeddings
 │
 ▼
Qdrant
 │
 │
 └───────────────┐
                 │
User question    │
      │          │
      ▼          │
Query embedding │
      │          │
      ▼          │
Similarity search
      │
      ▼
Retrieved chunks
      │
      ▼
Context builder
      │
      ▼
Ollama / local LLM
      │
      ▼
Answer + sources
```

The important design principle is that the LLM does not receive the whole document. It receives context retrieved from the vector store.

---

## Technology Stack

### Application

* Python 3.11
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings

### Document Processing

* PyMuPDF

### Embeddings

* Sentence Transformers
* `sentence-transformers/all-MiniLM-L6-v2`

### Vector Search

* Qdrant
* cosine similarity

### LLM

* Ollama
* currently configured for `llama3.1:8b`

### Testing

* Pytest
* FastAPI TestClient

### Infrastructure

* Docker Desktop
* Docker Compose
* Qdrant running as a Docker container

---

## Project Structure

```text
local-ai-platform/
│
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   ├── documents.py
│   │   └── main.py
│   │
│   ├── core/
│   │   └── config.py
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
│   └── retrieval/
│       ├── context.py
│       └── service.py
│
├── docs/
│   ├── architecture/
│   │   └── ADR-001-modular-monolith.md
│   └── requirements.md
│
├── scripts/
│   └── index_test_document.py
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
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Requirements

### Software

* Windows 11 or Linux
* Python 3.11+
* Docker Desktop
* Git
* Ollama

### Local Services

The MVP requires:

* Qdrant
* Ollama

The Python application itself runs locally in the virtual environment.

---

## Installation

Clone the repository and enter the project directory:

```powershell
git clone <repository-url>
cd local-ai-platform
```

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Configuration

The application can be configured using environment variables.

Example configuration is available in:

```text
.env.example
```

Current defaults:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

A local `.env` file is optional.

---

## Qdrant

Start Qdrant with Docker Compose:

```powershell
docker compose up -d
```

Check running containers:

```powershell
docker ps
```

The application expects Qdrant on:

```text
http://localhost:6333
```

Qdrant data is persisted using a Docker volume.

---

## Ollama

Make sure Ollama is installed and running.

Check available models:

```powershell
ollama list
```

The default model is:

```text
llama3.1:8b
```

Start the Ollama service if required:

```powershell
ollama serve
```

The model can be changed through the application configuration.

---

## Running the API

From the project root:

```powershell
uvicorn app.api.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI interactive documentation:

```text
http://localhost:8000/docs
```

---

## API

### Health Check

```http
GET /health
```

Example:

```json
{
  "status": "ok"
}
```

---

### Upload Document

```http
POST /documents/upload
```

The current MVP accepts PDF files.

Example using PowerShell:

```powershell
$form = @{
    file = Get-Item ".\test.pdf"
}

Invoke-RestMethod `
    -Uri "http://localhost:8000/documents/upload" `
    -Method Post `
    -Form $form
```

Example response:

```json
{
  "document_id": "...",
  "filename": "test.pdf",
  "content_type": "application/pdf",
  "page_count": 1,
  "chunk_count": 1,
  "indexed": true,
  "duplicate": false
}
```

The document ID is generated from the SHA-256 hash of the file contents.

This means uploading the same document again can be detected as a duplicate.

---

### Ask a Question

```http
POST /chat
```

Example request:

```json
{
  "question": "Ile kosztował rower Trek Rail 9?",
  "limit": 3
}
```

Example response:

```json
{
  "answer": "5 400,00",
  "sources": [
    {
      "chunk_id": "...",
      "document_id": "...",
      "filename": "test.pdf",
      "page_number": 1,
      "score": 0.72
    }
  ]
}
```

The response contains both the generated answer and metadata describing the retrieved source chunks.

---

## Testing

Run the complete test suite:

```powershell
pytest -q
```

Current test status:

```text
12 passed
```

The test suite covers:

* document model
* PDF extraction
* document metadata
* text chunking
* page-aware chunking
* embeddings
* vector retrieval
* real document retrieval
* document deduplication
* API validation
* API health endpoint
* document upload validation
* chat request validation

Some tests use the real embedding model and Qdrant instance, providing an integration-level check of the actual retrieval pipeline.

---

## Design Principles

### Local-first

The application is designed to work with locally running infrastructure whenever possible.

The current MVP uses:

* local Python application
* local Qdrant
* local embedding model
* local Ollama LLM

No mandatory cloud AI API is required.

### Modular monolith

The project intentionally starts as a modular monolith instead of introducing microservices prematurely.

The goal is to maintain:

* simple local development
* low operational complexity
* clear module boundaries
* fast iteration
* easy testing

The architecture can be split into independent services later if there is a real technical reason to do so.

### Provider-oriented design

The application keeps LLM, embedding and retrieval functionality in dedicated modules.

This provides a foundation for adding alternative providers and implementations later without coupling the entire application to a single model or infrastructure choice.

### Evidence-based answers

Retrieved document chunks are passed to the LLM as explicit context and source metadata is returned with the API response.

The intended behavior is to answer from retrieved evidence rather than relying on unsupported model knowledge.

### Reproducibility

The project tracks its Python dependencies in:

```text
requirements.txt
```

Infrastructure is defined through:

```text
docker-compose.yml
```

Application configuration is externalized through environment variables.

---

## Current Limitations

The current MVP is intentionally limited.

At the moment:

* only PDF documents are supported
* PDF extraction uses text extraction and does not yet provide OCR
* chunking is character-based
* retrieval uses vector similarity only
* there is no hybrid lexical/vector retrieval
* there is no reranking stage
* there is no evaluation dataset
* there is no authentication
* there is no multi-user or multi-tenant model
* there is no production frontend
* there is no agent/autonomous action layer
* LLM integration currently targets Ollama

These are deliberate scope decisions for the MVP rather than final architectural constraints.

---

## Roadmap

### Phase 1 — Foundation

* [x] project requirements
* [x] modular monolith architecture
* [x] Docker Compose infrastructure
* [x] application configuration
* [x] dependency manifest
* [x] basic automated tests

### Phase 2 — MVP Vertical Slice

* [x] PDF upload
* [x] document normalization
* [x] document identity
* [x] duplicate detection
* [x] text chunking
* [x] embeddings
* [x] Qdrant indexing
* [x] vector retrieval
* [x] context construction
* [x] Ollama integration
* [x] question answering
* [x] source metadata
* [x] API tests

### Phase 3 — Stabilization

* [ ] improve error handling
* [ ] improve logging
* [ ] improve configuration management
* [ ] clean up dependency warnings
* [ ] improve test isolation
* [ ] add more edge-case tests
* [ ] improve API response models

### Phase 4 — Document Platform

Planned document support:

* [ ] TXT
* [ ] DOCX
* [ ] HTML
* [ ] XLSX
* [ ] JPG
* [ ] PNG
* [ ] OCR
* [ ] document metadata
* [ ] document classification
* [ ] extraction strategies per document type

### Phase 5 — Retrieval Platform

Planned retrieval improvements:

* [ ] hybrid retrieval
* [ ] lexical search
* [ ] vector search
* [ ] reciprocal rank fusion
* [ ] reranking
* [ ] retrieval configuration
* [ ] retrieval evaluation
* [ ] benchmark datasets
* [ ] retrieval quality metrics

### Phase 6 — LLM Platform

Planned LLM improvements:

* [ ] provider interface
* [ ] multiple LLM providers
* [ ] model configuration
* [ ] generation parameters
* [ ] prompt management
* [ ] token usage metrics
* [ ] latency metrics
* [ ] structured generation

### Phase 7 — AI Applications

Potential applications built on top of the platform:

* General Assistant
* System Analyst
* Document Analyst
* Knowledge Assistant
* specialized domain assistants
* future agent-based workflows

### Phase 8 — Evaluation & Portfolio

* [ ] benchmark datasets
* [ ] retrieval evaluation
* [ ] answer quality evaluation
* [ ] regression tests
* [ ] performance measurements
* [ ] architecture documentation
* [ ] technical case studies
* [ ] production-style documentation

---

## Project Goal

The goal is not to build another isolated PDF chatbot.

The goal is to develop a reusable **local AI application platform** that demonstrates how document processing, retrieval, embeddings, vector databases and local LLMs can be combined into maintainable AI systems.

The project is also intended as a practical portfolio project demonstrating:

* Python application architecture
* REST API development
* RAG system design
* vector databases
* local LLM integration
* document processing
* automated testing
* Docker-based infrastructure
* configuration management
* incremental system evolution

---

## Development Philosophy

The project follows a simple principle:

> **Build a working vertical slice first, then make it robust and extensible.**

Instead of starting with distributed infrastructure, complex orchestration or premature abstractions, the system is developed incrementally around real working functionality.

The expected evolution is:

```text
Working MVP
    ↓
Stabilization
    ↓
More document types
    ↓
Better retrieval
    ↓
Provider abstraction
    ↓
Evaluation
    ↓
AI applications
```

This approach keeps the project usable at every stage while allowing the architecture to evolve based on actual requirements.

---

## License

License information will be added before the first formal public release.
