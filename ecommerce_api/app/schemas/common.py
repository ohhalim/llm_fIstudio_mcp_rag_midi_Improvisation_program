from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    success: bool = False


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    data: List[Any]


class HealthCheck(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime
    database: Optional[str] = None
    redis: Optional[str] = None


class SearchParams(BaseModel):
    q: Optional[str] = Field(None, description="Search query")
    sort_by: Optional[str] = Field("created_at", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="Sort order (asc/desc)")


class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int
    content_type: str
    upload_url: str
    created_at: datetime


class BulkOperationResponse(BaseModel):
    success_count: int
    error_count: int
    total_count: int
    errors: Optional[List[Dict[str, Any]]] = None


class StatusUpdate(BaseModel):
    status: str
    updated_at: datetime
    updated_by: Optional[int] = None
    notes: Optional[str] = None