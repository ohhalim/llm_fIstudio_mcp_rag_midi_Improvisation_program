from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Document 스키마
class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    document_type: str = Field(..., regex="^(music_theory|tutorial|article|reference)$")
    source_url: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = Field(None, regex="^(beginner|intermediate|advanced)$")

class DocumentCreate(DocumentBase):
    is_public: bool = False

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    document_type: Optional[str] = Field(None, regex="^(music_theory|tutorial|article|reference)$")
    source_url: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = Field(None, regex="^(beginner|intermediate|advanced)$")
    is_public: Optional[bool] = None

class Document(DocumentBase):
    id: int
    user_id: int
    embedding_id: Optional[str] = None
    chunk_count: int
    is_processed: bool
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Query 스키마
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    max_results: Optional[int] = Field(default=5, ge=1, le=20)
    similarity_threshold: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    document_types: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    difficulty_levels: Optional[List[str]] = None
    include_metadata: bool = False

class SearchResult(BaseModel):
    document_id: int
    chunk_id: int
    content: str
    similarity_score: float
    document_title: str
    document_type: str
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    query: str
    response: str
    search_results: List[SearchResult]
    total_results: int
    search_time: float
    generation_time: float
    total_time: float
    model_used: str

# Knowledge Base 스키마
class KnowledgeBaseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    is_private: bool = True

class KnowledgeBaseCreate(KnowledgeBaseBase):
    allowed_users: Optional[List[int]] = None

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_private: Optional[bool] = None
    allowed_users: Optional[List[int]] = None

class KnowledgeBase(KnowledgeBaseBase):
    id: int
    user_id: int
    allowed_users: Optional[List[int]] = None
    document_count: int
    total_chunks: int
    last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# RAG Settings 스키마
class RagSettingsBase(BaseModel):
    default_max_results: int = Field(default=5, ge=1, le=20)
    default_similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    chunk_size: int = Field(default=512, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)
    default_model: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=1000, ge=100, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    preferred_language: str = Field(default="ko", regex="^(ko|en|ja|zh)$")

class RagSettingsCreate(RagSettingsBase):
    pass

class RagSettingsUpdate(RagSettingsBase):
    pass

class RagSettings(RagSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 응답 스키마
class DocumentUploadResponse(BaseModel):
    document: Document
    message: str = "Document uploaded and processed successfully"

class DocumentsListResponse(BaseModel):
    documents: List[Document]
    total: int
    page: int
    size: int

class KnowledgeBasesListResponse(BaseModel):
    knowledge_bases: List[KnowledgeBase]
    total: int
    page: int
    size: int

class QueryHistoryResponse(BaseModel):
    id: int
    query: str
    response: str
    search_results: List[Dict[str, Any]]
    search_time: float
    generation_time: float
    total_time: float
    relevance_score: Optional[float] = None
    user_rating: Optional[int] = None
    created_at: datetime

class QueryHistoryListResponse(BaseModel):
    queries: List[QueryHistoryResponse]
    total: int
    page: int
    size: int

class MessageResponse(BaseModel):
    message: str

# 검색 및 추천 스키마
class RecommendationRequest(BaseModel):
    user_interests: Optional[List[str]] = None
    difficulty_level: Optional[str] = Field(None, regex="^(beginner|intermediate|advanced)$")
    document_types: Optional[List[str]] = None
    limit: int = Field(default=10, ge=1, le=50)

class RecommendationResponse(BaseModel):
    recommendations: List[Document]
    reason: str
    total_found: int

class SimilarDocumentsRequest(BaseModel):
    document_id: int
    similarity_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    limit: int = Field(default=5, ge=1, le=20)

class SimilarDocumentsResponse(BaseModel):
    similar_documents: List[Dict[str, Any]]
    source_document: Document
    total_found: int