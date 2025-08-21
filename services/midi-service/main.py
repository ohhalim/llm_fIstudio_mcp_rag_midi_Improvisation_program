from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import sys
import shutil
import json
from pathlib import Path
from typing import Optional, List

# 공통 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.config import get_settings
from shared.database import init_database, get_db
from shared.logging import setup_logging, get_logger, logging_middleware

from .models import MidiFile, MidiAnalysis, GeneratedMidi, UserPreferences
from .schemas import (
    MidiFileCreate, MidiFileUpdate, MidiFile as MidiFileSchema,
    MidiAnalysisRequest, MidiAnalysis as MidiAnalysisSchema,
    MidiGenerationRequest, MidiGenerationResponse,
    UserPreferencesCreate, UserPreferencesUpdate, UserPreferences as UserPreferencesSchema,
    MidiUploadResponse, MidiFilesListResponse, GeneratedMidiListResponse, MessageResponse
)
from .midi_processor import MidiProcessor

# 설정 초기화
settings = get_settings("midi-service", 8002)
setup_logging("midi-service")
logger = get_logger(__name__)

# 데이터베이스 초기화
db_manager = init_database(settings.db)

# MIDI 프로세서 초기화
midi_processor = MidiProcessor()

# 파일 저장 경로
UPLOAD_DIR = Path("./uploads/midi")
GENERATED_DIR = Path("./generated/midi")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="MIDI Service",
    description="MIDI 처리 및 생성 마이크로서비스",
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
    logger.info("MIDI Service starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("MIDI Service shutting down")

def get_current_user_from_header(request):
    """헤더에서 현재 사용자 정보 추출 (Gateway에서 전달)"""
    user_id = request.headers.get("X-User-ID")
    user_email = request.headers.get("X-User-Email")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {"sub": int(user_id), "email": user_email}

# 헬스 체크
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "midi-service"}

# MIDI 파일 업로드
@app.post("/api/midi/upload", response_model=MidiUploadResponse)
async def upload_midi_file(
    request,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    artist: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """MIDI 파일 업로드"""
    user_info = get_current_user_from_header(request)
    
    # 파일 확장자 검사
    if not file.filename.lower().endswith(('.mid', '.midi')):
        raise HTTPException(status_code=400, detail="Only MIDI files are allowed")
    
    try:
        # 파일 저장
        file_path = UPLOAD_DIR / f"{user_info['sub']}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # MIDI 파일 유효성 검사
        if not midi_processor.validate_midi_file(str(file_path)):
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Invalid MIDI file")
        
        # 메타데이터 추출
        metadata = midi_processor.extract_metadata(str(file_path))
        
        # 데이터베이스에 저장
        midi_file = MidiFile(
            user_id=user_info['sub'],
            filename=file.filename,
            original_filename=file.filename,
            file_size=file_path.stat().st_size,
            file_path=str(file_path),
            duration=metadata.get('duration'),
            bpm=metadata.get('bpm'),
            time_signature=metadata.get('time_signature'),
            key_signature=metadata.get('key_signature'),
            track_count=metadata.get('track_count', 0),
            instrument_list=json.dumps(metadata.get('instruments', [])),
            title=title or metadata.get('title'),
            artist=artist or metadata.get('artist'),
            genre=genre,
            processed=True
        )
        
        db.add(midi_file)
        db.commit()
        db.refresh(midi_file)
        
        # JSON 역직렬화
        if midi_file.instrument_list:
            midi_file.instrument_list = json.loads(midi_file.instrument_list)
        
        return MidiUploadResponse(midi_file=midi_file)
        
    except Exception as e:
        # 에러 발생 시 파일 삭제
        if file_path.exists():
            os.remove(file_path)
        logger.error(f"MIDI upload failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# MIDI 파일 목록 조회
@app.get("/api/midi/files", response_model=MidiFilesListResponse)
async def get_midi_files(
    request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """사용자 MIDI 파일 목록 조회"""
    user_info = get_current_user_from_header(request)
    
    files = db.query(MidiFile).filter(
        MidiFile.user_id == user_info['sub']
    ).offset(skip).limit(limit).all()
    
    total = db.query(MidiFile).filter(
        MidiFile.user_id == user_info['sub']
    ).count()
    
    # JSON 역직렬화
    for file in files:
        if file.instrument_list:
            file.instrument_list = json.loads(file.instrument_list)
    
    return MidiFilesListResponse(
        midi_files=files,
        total=total,
        page=skip // limit + 1,
        size=len(files)
    )

# MIDI 파일 분석
@app.post("/api/midi/{file_id}/analyze", response_model=MidiAnalysisSchema)
async def analyze_midi_file(
    file_id: int,
    request,
    analysis_request: MidiAnalysisRequest,
    db: Session = Depends(get_db)
):
    """MIDI 파일 분석"""
    user_info = get_current_user_from_header(request)
    
    # 파일 존재 확인
    midi_file = db.query(MidiFile).filter(
        MidiFile.id == file_id,
        MidiFile.user_id == user_info['sub']
    ).first()
    
    if not midi_file:
        raise HTTPException(status_code=404, detail="MIDI file not found")
    
    try:
        analysis_results = {}
        
        # 화성 분석
        if analysis_request.analyze_harmony:
            harmony_analysis = midi_processor.analyze_harmony(midi_file.file_path)
            analysis_results.update(harmony_analysis)
        
        # 기존 분석 삭제 후 새로 생성
        db.query(MidiAnalysis).filter(
            MidiAnalysis.midi_file_id == file_id
        ).delete()
        
        analysis = MidiAnalysis(
            midi_file_id=file_id,
            user_id=user_info['sub'],
            chord_progression=json.dumps(analysis_results.get('chord_progression', [])),
            harmony_analysis=json.dumps(analysis_results),
            analysis_model="basic_midi_analysis",
            confidence_score=0.8
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # JSON 역직렬화
        if analysis.chord_progression:
            analysis.chord_progression = json.loads(analysis.chord_progression)
        if analysis.harmony_analysis:
            analysis.harmony_analysis = json.loads(analysis.harmony_analysis)
        
        return analysis
        
    except Exception as e:
        logger.error(f"MIDI analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# MIDI 생성
@app.post("/api/midi/generate", response_model=MidiGenerationResponse)
async def generate_midi(
    request,
    generation_request: MidiGenerationRequest,
    db: Session = Depends(get_db)
):
    """MIDI 생성/즉흥연주"""
    user_info = get_current_user_from_header(request)
    
    try:
        if generation_request.generation_type == "improvisation":
            # 원본 파일 확인
            if not generation_request.source_midi_id:
                raise HTTPException(status_code=400, detail="Source MIDI file required for improvisation")
            
            source_file = db.query(MidiFile).filter(
                MidiFile.id == generation_request.source_midi_id,
                MidiFile.user_id == user_info['sub']
            ).first()
            
            if not source_file:
                raise HTTPException(status_code=404, detail="Source MIDI file not found")
            
            # 즉흥연주 생성
            generated_file_path = midi_processor.generate_improvisation(
                source_file.file_path,
                style=generation_request.style or "jazz",
                complexity=generation_request.complexity or "medium",
                duration=generation_request.duration or 30
            )
        else:
            raise HTTPException(status_code=400, detail="Generation type not supported yet")
        
        # 생성된 파일을 저장 디렉토리로 이동
        filename = f"generated_{user_info['sub']}_{generation_request.generation_type}.mid"
        final_path = GENERATED_DIR / filename
        shutil.move(generated_file_path, final_path)
        
        # 데이터베이스에 저장
        generated_midi = GeneratedMidi(
            user_id=user_info['sub'],
            source_midi_id=generation_request.source_midi_id,
            generation_type=generation_request.generation_type,
            prompt=generation_request.prompt,
            style=generation_request.style,
            filename=filename,
            file_path=str(final_path),
            file_size=final_path.stat().st_size,
            generation_params=json.dumps(generation_request.model_dump()),
            model_name="basic_improvisation_model",
            model_version="1.0"
        )
        
        db.add(generated_midi)
        db.commit()
        db.refresh(generated_midi)
        
        # JSON 역직렬화
        if generated_midi.generation_params:
            generated_midi.generation_params = json.loads(generated_midi.generation_params)
        
        download_url = f"/api/midi/download/{generated_midi.id}"
        
        return MidiGenerationResponse(
            generated_midi=generated_midi,
            download_url=download_url
        )
        
    except Exception as e:
        logger.error(f"MIDI generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

# 생성된 MIDI 다운로드
@app.get("/api/midi/download/{generated_id}")
async def download_generated_midi(
    generated_id: int,
    request,
    db: Session = Depends(get_db)
):
    """생성된 MIDI 파일 다운로드"""
    user_info = get_current_user_from_header(request)
    
    generated_midi = db.query(GeneratedMidi).filter(
        GeneratedMidi.id == generated_id,
        GeneratedMidi.user_id == user_info['sub']
    ).first()
    
    if not generated_midi:
        raise HTTPException(status_code=404, detail="Generated MIDI not found")
    
    if not Path(generated_midi.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        generated_midi.file_path,
        media_type="audio/midi",
        filename=generated_midi.filename
    )

# 생성된 MIDI 목록
@app.get("/api/midi/generated", response_model=GeneratedMidiListResponse)
async def get_generated_midi(
    request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """생성된 MIDI 목록 조회"""
    user_info = get_current_user_from_header(request)
    
    generated_files = db.query(GeneratedMidi).filter(
        GeneratedMidi.user_id == user_info['sub']
    ).offset(skip).limit(limit).all()
    
    total = db.query(GeneratedMidi).filter(
        GeneratedMidi.user_id == user_info['sub']
    ).count()
    
    # JSON 역직렬화
    for file in generated_files:
        if file.generation_params:
            file.generation_params = json.loads(file.generation_params)
    
    return GeneratedMidiListResponse(
        generated_midi=generated_files,
        total=total,
        page=skip // limit + 1,
        size=len(generated_files)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.service.service_host,
        port=settings.service.service_port,
        reload=settings.service.debug,
        log_config=None
    )