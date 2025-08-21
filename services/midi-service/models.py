from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, LargeBinary
from sqlalchemy.sql import func
import sys
import os

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import Base

class MidiFile(Base):
    __tablename__ = "midi_files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    duration = Column(Float)  # 재생 시간 (초)
    
    # MIDI 메타데이터
    title = Column(String(200))
    artist = Column(String(200))
    genre = Column(String(100))
    bpm = Column(Float)  # BPM (Beats Per Minute)
    time_signature = Column(String(10))  # 4/4, 3/4 등
    key_signature = Column(String(10))  # C, Am 등
    
    # 트랙 정보
    track_count = Column(Integer, default=0)
    instrument_list = Column(Text)  # JSON 문자열로 저장
    
    # 파일 경로 및 상태
    file_path = Column(String(500), nullable=False)
    processed = Column(Boolean, default=False)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MidiAnalysis(Base):
    __tablename__ = "midi_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    midi_file_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # 분석 결과
    chord_progression = Column(Text)  # JSON 문자열
    melody_analysis = Column(Text)  # JSON 문자열
    rhythm_analysis = Column(Text)  # JSON 문자열
    harmony_analysis = Column(Text)  # JSON 문자열
    
    # 음악 이론 분석
    scale_analysis = Column(Text)  # JSON 문자열
    modulations = Column(Text)  # JSON 문자열
    
    # AI 분석 메타데이터
    analysis_model = Column(String(100))
    confidence_score = Column(Float)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class GeneratedMidi(Base):
    __tablename__ = "generated_midi"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    source_midi_id = Column(Integer, index=True)  # 원본 MIDI (improvisation의 경우)
    
    # 생성 정보
    generation_type = Column(String(50), nullable=False)  # 'improvisation', 'composition', 'variation'
    prompt = Column(Text)  # 사용자 프롬프트
    style = Column(String(100))  # 음악 스타일
    
    # 생성된 파일 정보
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    duration = Column(Float)
    
    # 생성 매개변수
    generation_params = Column(Text)  # JSON 문자열로 저장
    
    # AI 모델 정보
    model_name = Column(String(100))
    model_version = Column(String(50))
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserPreferences(Base):
    __tablename__ = "user_midi_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    
    # 선호 설정
    preferred_styles = Column(Text)  # JSON 배열
    preferred_instruments = Column(Text)  # JSON 배열
    preferred_tempo_range = Column(String(20))  # "60-120" 형태
    preferred_key_signatures = Column(Text)  # JSON 배열
    
    # 생성 기본값
    default_duration = Column(Integer, default=30)  # 기본 생성 길이 (초)
    default_complexity = Column(String(20), default="medium")  # low, medium, high
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())