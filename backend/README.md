# CustomerLens Backend

This backend provides the enterprise architecture for a customer intelligence platform built with FastAPI, RAG, machine learning, and AI agents.

## Structure

- app/: FastAPI application, configuration, and dependency wiring
- api/: HTTP endpoints for upload, query, dashboard, and prediction
- core/: logging and custom exceptions
- services/: domain services with placeholder interfaces
- agents/: specialized AI agent modules
- models/: Pydantic request and response models
- database/: SQLAlchemy access and schemas
- rag/: chunking, embeddings, vector store, and retrieval abstractions
- ml/: segmentation, churn prediction, and forecasting services
- utils/: file loading and validation helpers
- tests/: pytest smoke tests

## Notes

Business logic is intentionally left as placeholders. This scaffold is designed for extension into a production backend.
