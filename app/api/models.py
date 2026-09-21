from pydantic import BaseModel


class SourceResponse(BaseModel):
    chunk_id: str | None = None
    document_id: str | None = None
    filename: str | None = None
    page_number: int | None = None
    score: float | None = None


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    content_type: str
    page_count: int
    chunk_count: int
    indexed: bool
    duplicate: bool


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]