# ADR-001 — Modular Monolith as Initial Architecture

* **Status:** Accepted
* **Date:** 2026-09-14
* **Decision:** Use a modular monolith as the initial architecture of `local-ai-platform`.

## Context

`local-ai-platform` is intended to become a local-first AI platform combining document processing, retrieval, local LLM inference and AI-assisted interaction.

The project is initially a personal and portfolio project. It should remain simple enough to develop, test and run locally, while providing clear architectural boundaries that allow future expansion.

The platform is expected to evolve over time. Possible future changes include:

* additional LLM providers,
* different embedding providers,
* different vector stores,
* keyword and hybrid retrieval,
* reranking,
* additional document processors,
* background workers,
* multiple AI agents,
* cloud providers,
* more advanced storage,
* independent services for selected components.

Starting immediately with a distributed microservice architecture would introduce unnecessary operational complexity before the system and its boundaries are well understood.

## Decision

We will implement `local-ai-platform` initially as a **modular monolith**.

The application will run as a single logical application, while its internal code will be divided into clearly defined modules with explicit responsibilities.

Initial conceptual modules:

* API
* Documents
* Retrieval
* Inference
* Storage
* Agents

Important external dependencies will be accessed through interfaces where practical.

Examples include:

```text
LLMProvider
EmbeddingProvider
Retriever
Reranker
DocumentProcessor
```

Concrete implementations such as Ollama, FAISS or specific document parsers should not leak unnecessarily into unrelated application modules.

## Rationale

This approach provides a balance between simplicity and extensibility.

### Simplicity

The project can initially be developed and deployed as a single application without requiring:

* multiple independently deployed services,
* service discovery,
* message brokers,
* distributed tracing,
* Kubernetes,
* complex networking,
* multiple deployment pipelines.

### Extensibility

Clear module boundaries make it possible to replace or extend individual implementations.

For example:

```text
LLMProvider
    ├── OllamaProvider
    ├── CloudProvider
    └── FutureProvider
```

and:

```text
Retriever
    ├── VectorRetriever
    ├── KeywordRetriever
    └── HybridRetriever
```

The rest of the application should depend on the abstraction rather than a specific implementation whenever this provides meaningful architectural value.

### Experimentation

The platform is intended not only to run AI workloads but also to measure and compare different approaches.

The architecture should therefore make it possible to experiment with:

* different LLM providers,
* different embedding models,
* different retrieval strategies,
* reranking,
* local versus cloud inference,
* different storage technologies.

## Consequences

### Positive

* Lower initial complexity.
* Easier local development.
* Easier testing.
* Easier Docker-based deployment.
* Clear architectural boundaries.
* Easier replacement of selected technologies.
* Good foundation for future evolution.
* Suitable for a portfolio project where architectural decisions should remain understandable.

### Negative

* Module boundaries must be actively maintained.
* A modular monolith can still become tightly coupled if dependencies are not controlled.
* Some future scaling scenarios may require extracting individual modules into separate services.
* Interfaces introduce some additional code and design effort.

## Future Evolution

We will not introduce microservices simply because the project grows.

A module may be extracted into an independent service only when there is a concrete reason, such as:

* independent scaling requirements,
* independent deployment requirements,
* resource isolation,
* asynchronous workload requirements,
* operational requirements,
* or a clear architectural benefit.

The default assumption is therefore:

> Keep the system modular first. Distribute it only when there is a demonstrated need.

## Related Principles

This decision supports the following project principles:

* Local-first
* Interfaces over implementations
* Measure before optimizing
* Simple before distributed
* Reproducibility
* Modularity
* Maintainability
