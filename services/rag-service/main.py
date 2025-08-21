from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import sys
import json
from typing import Optional, List
import time

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.config import get_settings
from shared.database import init_database, get_db
from shared.logging import setup_logging, get_logger, logging_middleware

from .models import Document, DocumentChunk, QueryHistory, KnowledgeBase, RagSettings
from .schemas import (
    DocumentCreate, DocumentUpdate, Document as DocumentSchema,
    QueryRequest, QueryResponse, QueryHistoryResponse, QueryHistoryListResponse,
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBase as KnowledgeBaseSchema,
    RagSettingsCreate, RagSettingsUpdate, RagSettings as RagSettingsSchema,
    DocumentUploadResponse, DocumentsListResponse, KnowledgeBasesListResponse,
    RecommendationRequest, RecommendationResponse,
    SimilarDocumentsRequest, SimilarDocumentsResponse,
    MessageResponse
)
from .vector_store import VectorStore
from .rag_engine import RAGEngine

# 설정 초기화
settings = get_settings("rag-service", 8003)
setup_logging("rag-service")
logger = get_logger(__name__)

# 데이터베이스 초기화
db_manager = init_database(settings.db)

# RAG 엔진 초기화
vector_store = VectorStore()
rag_engine = RAGEngine(
    vector_store=vector_store,
    api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

app = FastAPI(
    title="RAG Service",
    description="검색 증강 생성 마이크로서비스",
    version="1.0.0"
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 미들웨어
app.middleware("http")(logging_middleware)

@app.on_event("startup")
async def startup_event():
    await db_manager.create_tables()
    logger.info("RAG Service starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("RAG Service shutting down")

def get_current_user_from_header(request):
    """헤더에서 현재 사용자 정보 추출 (Gateway에서 전달)"""
    user_id = request.headers.get("X-User-ID")
    user_email = request.headers.get("X-User-Email")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {"sub": int(user_id), "email": user_email}

def get_user_settings(db: Session, user_id: int) -> RagSettings:
    """사용자 RAG 설정 조회 또는 기본값 반환"""
    settings_obj = db.query(RagSettings).filter(RagSettings.user_id == user_id).first()
    if not settings_obj:
        # 기본 설정 생성
        settings_obj = RagSettings(user_id=user_id)
        db.add(settings_obj)
        db.commit()
        db.refresh(settings_obj)
    return settings_obj

# 헬스 체크
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-service"}

# 문서 업로드
@app.post("/api/rag/documents", response_model=DocumentUploadResponse)
async def upload_document(
    request,
    title: str = Form(...),
    content: str = Form(...),
    document_type: str = Form(...),
    source_url: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON 문자열
    category: Optional[str] = Form(None),
    difficulty_level: Optional[str] = Form(None),
    is_public: bool = Form(False),
    db: Session = Depends(get_db)
):
    """문서 업로드 및 벡터화"""
    user_info = get_current_user_from_header(request)
    
    try:
        # 태그 파싱
        tags_list = None
        if tags:
            try:
                tags_list = json.loads(tags)
            except json.JSONDecodeError:
                tags_list = [tag.strip() for tag in tags.split(',')]
        
        # 문서 데이터베이스에 저장
        document = Document(
            user_id=user_info['sub'],
            title=title,
            content=content,
            document_type=document_type,
            source_url=source_url,
            author=author,
            tags=tags_list,
            category=category,
            difficulty_level=difficulty_level,
            is_public=is_public
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # 벡터화 및 청킹
        collection_name = f"user_{user_info['sub']}"
        metadata = {
            'document_id': document.id,
            'title': document.title,
            'document_type': document.document_type,
            'category': document.category,
            'difficulty_level': document.difficulty_level,
            'author': document.author,
            'tags': document.tags,
            'user_id': user_info['sub']
        }
        
        chunk_ids = rag_engine.process_document(
            document_id=document.id,
            content=content,
            metadata=metadata,
            collection_name=collection_name
        )
        
        # 문서 처리 완료 표시
        document.is_processed = True
        document.chunk_count = len(chunk_ids)
        document.embedding_id = f"doc_{document.id}"
        
        db.commit()
        db.refresh(document)
        
        return DocumentUploadResponse(document=document)
        
    except Exception as e:
        logger.error(f"Document upload failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# 문서 목록 조회
@app.get("/api/rag/documents", response_model=DocumentsListResponse)
async def get_documents(
    request,
    skip: int = 0,
    limit: int = 100,
    document_type: Optional[str] = None,
    category: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """사용자 문서 목록 조회"""
    user_info = get_current_user_from_header(request)
    
    query = db.query(Document).filter(Document.user_id == user_info['sub'])
    
    # 필터 적용
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if category:
        query = query.filter(Document.category == category)
    if difficulty_level:
        query = query.filter(Document.difficulty_level == difficulty_level)
    
    documents = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return DocumentsListResponse(
        documents=documents,
        total=total,
        page=skip // limit + 1,
        size=len(documents)
    )

# 질의응답
@app.post("/api/rag/query", response_model=QueryResponse)
async def query_documents(
    request,
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """문서 검색 및 응답 생성"""
    user_info = get_current_user_from_header(request)
    user_settings = get_user_settings(db, user_info['sub'])
    
    try:
        # 필터 구성
        filters = {'user_id': user_info['sub']}
        
        if query_request.document_types:
            filters['document_type'] = {"$in": query_request.document_types}
        if query_request.categories:
            filters['category'] = {"$in": query_request.categories}
        if query_request.difficulty_levels:
            filters['difficulty_level'] = {"$in": query_request.difficulty_levels}
        
        if query_request.include_metadata:
            filters['include_metadata'] = True
        
        # RAG 실행
        result = rag_engine.search_and_generate(
            query=query_request.query,
            collection_name=f"user_{user_info['sub']}",
            max_results=query_request.max_results or user_settings.default_max_results,
            similarity_threshold=query_request.similarity_threshold or user_settings.default_similarity_threshold,
            model=user_settings.default_model,
            max_tokens=user_settings.max_tokens,
            temperature=user_settings.temperature,
            filters=filters
        )
        
        # 쿼리 히스토리 저장
        query_history = QueryHistory(
            user_id=user_info['sub'],
            query=query_request.query,
            search_results=result['search_results'],
            response=result['response'],
            search_time=result['search_time'],
            generation_time=result['generation_time'],
            total_time=result['total_time'],
            model_used=result['model_used'],
            max_results=query_request.max_results or user_settings.default_max_results,
            similarity_threshold=query_request.similarity_threshold or user_settings.default_similarity_threshold
        )
        
        db.add(query_history)
        db.commit()
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Query processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# 추천 시스템
@app.post("/api/rag/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    request,
    recommendation_request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """사용자 맞춤 문서 추천"""
    user_info = get_current_user_from_header(request)
    
    try:
        recommendations = rag_engine.get_recommendations(
            user_interests=recommendation_request.user_interests or ["음악", "MIDI"],
            collection_name=f"user_{user_info['sub']}",
            difficulty_level=recommendation_request.difficulty_level,
            document_types=recommendation_request.document_types,
            limit=recommendation_request.limit
        )
        
        # 문서 정보 보완
        recommended_docs = []
        for rec in recommendations:
            doc = db.query(Document).filter(Document.id == rec['document_id']).first()
            if doc:
                recommended_docs.append(doc)
        
        reason = f"사용자 관심사 '{', '.join(recommendation_request.user_interests or ['음악', 'MIDI'])}'를 기반으로 추천"
        
        return RecommendationResponse(
            recommendations=recommended_docs,
            reason=reason,
            total_found=len(recommended_docs)
        )
        
    except Exception as e:
        logger.error(f"Recommendation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

# 유사 문서 찾기
@app.post("/api/rag/similar", response_model=SimilarDocumentsResponse)
async def find_similar_documents(
    request,
    similar_request: SimilarDocumentsRequest,
    db: Session = Depends(get_db)
):
    """유사 문서 찾기"""
    user_info = get_current_user_from_header(request)
    
    # 원본 문서 확인
    source_doc = db.query(Document).filter(
        Document.id == similar_request.document_id,
        Document.user_id == user_info['sub']
    ).first()
    
    if not source_doc:
        raise HTTPException(status_code=404, detail="Source document not found")
    
    try:
        similar_docs = rag_engine.find_similar_documents(
            document_id=similar_request.document_id,
            collection_name=f"user_{user_info['sub']}",
            similarity_threshold=similar_request.similarity_threshold,
            limit=similar_request.limit
        )
        
        return SimilarDocumentsResponse(
            similar_documents=similar_docs,
            source_document=source_doc,
            total_found=len(similar_docs)
        )
        
    except Exception as e:
        logger.error(f"Similar document search failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Similar search failed: {str(e)}")

# 쿼리 히스토리
@app.get("/api/rag/history", response_model=QueryHistoryListResponse)
async def get_query_history(
    request,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """쿼리 히스토리 조회"""
    user_info = get_current_user_from_header(request)
    
    queries = db.query(QueryHistory).filter(
        QueryHistory.user_id == user_info['sub']
    ).order_by(QueryHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    total = db.query(QueryHistory).filter(
        QueryHistory.user_id == user_info['sub']
    ).count()
    
    return QueryHistoryListResponse(
        queries=queries,
        total=total,
        page=skip // limit + 1,
        size=len(queries)
    )

# RAG 설정
@app.get("/api/rag/settings", response_model=RagSettingsSchema)
async def get_rag_settings(request, db: Session = Depends(get_db)):
    """RAG 설정 조회"""
    user_info = get_current_user_from_header(request)
    settings_obj = get_user_settings(db, user_info['sub'])
    return settings_obj

@app.put("/api/rag/settings", response_model=RagSettingsSchema)
async def update_rag_settings(
    request,
    settings_update: RagSettingsUpdate,
    db: Session = Depends(get_db)
):
    """RAG 설정 업데이트"""
    user_info = get_current_user_from_header(request)
    settings_obj = get_user_settings(db, user_info['sub'])
    
    update_data = settings_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings_obj, field, value)
    
    db.commit()
    db.refresh(settings_obj)
    
    return settings_obj

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.service.service_host,
        port=settings.service.service_port,
        reload=settings.service.debug,
        log_config=None
    )