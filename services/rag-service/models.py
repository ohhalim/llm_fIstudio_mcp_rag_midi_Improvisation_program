from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.sql import func
import sys
import os

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(50), nullable=False)  # 'music_theory', 'tutorial', 'article', 'reference'
    
    # 메타데이터
    source_url = Column(String(500))
    author = Column(String(200))
    tags = Column(JSON)  # 태그 목록
    category = Column(String(100))
    difficulty_level = Column(String(20))  # 'beginner', 'intermediate', 'advanced'
    
    # 벡터 정보
    embedding_id = Column(String(100), index=True)  # 벡터 DB에서의 ID
    chunk_count = Column(Integer, default=1)
    
    # 상태
    is_processed = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    
    # 벡터 정보
    embedding_id = Column(String(100), unique=True, index=True)
    vector_dimension = Column(Integer, default=384)  # sentence-transformers 기본값
    
    # 청크 메타데이터
    start_position = Column(Integer)
    end_position = Column(Integer)
    token_count = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    query = Column(Text, nullable=False)
    
    # 검색 결과
    search_results = Column(JSON)  # 검색된 문서들의 메타데이터
    response = Column(Text)  # 생성된 응답
    
    # 성능 메트릭
    search_time = Column(Float)  # 검색 소요 시간 (초)
    generation_time = Column(Float)  # 생성 소요 시간 (초)
    total_time = Column(Float)  # 총 소요 시간 (초)
    
    # 품질 메트릭
    relevance_score = Column(Float)  # 관련성 점수
    user_rating = Column(Integer)  # 사용자 평가 (1-5)
    
    # 설정
    model_used = Column(String(100))
    max_results = Column(Integer, default=5)
    similarity_threshold = Column(Float, default=0.7)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 설정
    is_private = Column(Boolean, default=True)
    allowed_users = Column(JSON)  # 접근 권한이 있는 사용자 ID 목록
    
    # 통계
    document_count = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RagSettings(Base):
    __tablename__ = "rag_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    
    # 검색 설정
    default_max_results = Column(Integer, default=5)
    default_similarity_threshold = Column(Float, default=0.7)
    chunk_size = Column(Integer, default=512)
    chunk_overlap = Column(Integer, default=50)
    
    # 생성 설정
    default_model = Column(String(100), default="gpt-3.5-turbo")
    max_tokens = Column(Integer, default=1000)
    temperature = Column(Float, default=0.7)
    
    # 언어 설정
    preferred_language = Column(String(10), default="ko")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())