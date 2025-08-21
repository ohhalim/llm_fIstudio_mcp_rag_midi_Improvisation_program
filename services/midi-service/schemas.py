from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# MIDI 파일 스키마
class MidiFileBase(BaseModel):
    filename: str
    title: Optional[str] = None
    artist: Optional[str] = None
    genre: Optional[str] = None

class MidiFileCreate(MidiFileBase):
    pass

class MidiFileUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    genre: Optional[str] = None

class MidiFile(MidiFileBase):
    id: int
    user_id: int
    original_filename: str
    file_size: int
    duration: Optional[float] = None
    bpm: Optional[float] = None
    time_signature: Optional[str] = None
    key_signature: Optional[str] = None
    track_count: int
    instrument_list: Optional[List[str]] = None
    processed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# MIDI 분석 스키마
class MidiAnalysisBase(BaseModel):
    chord_progression: Optional[List[Dict[str, Any]]] = None
    melody_analysis: Optional[Dict[str, Any]] = None
    rhythm_analysis: Optional[Dict[str, Any]] = None
    harmony_analysis: Optional[Dict[str, Any]] = None
    scale_analysis: Optional[Dict[str, Any]] = None
    modulations: Optional[List[Dict[str, Any]]] = None

class MidiAnalysisCreate(MidiAnalysisBase):
    midi_file_id: int

class MidiAnalysis(MidiAnalysisBase):
    id: int
    midi_file_id: int
    user_id: int
    analysis_model: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 생성된 MIDI 스키마
class GeneratedMidiBase(BaseModel):
    generation_type: str = Field(..., regex="^(improvisation|composition|variation)$")
    prompt: Optional[str] = None
    style: Optional[str] = None

class GeneratedMidiCreate(GeneratedMidiBase):
    source_midi_id: Optional[int] = None
    generation_params: Optional[Dict[str, Any]] = None

class GeneratedMidi(GeneratedMidiBase):
    id: int
    user_id: int
    source_midi_id: Optional[int] = None
    filename: str
    file_size: int
    duration: Optional[float] = None
    generation_params: Optional[Dict[str, Any]] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# 사용자 선호 설정 스키마
class UserPreferencesBase(BaseModel):
    preferred_styles: Optional[List[str]] = None
    preferred_instruments: Optional[List[str]] = None
    preferred_tempo_range: Optional[str] = None
    preferred_key_signatures: Optional[List[str]] = None
    default_duration: Optional[int] = Field(default=30, ge=10, le=300)
    default_complexity: Optional[str] = Field(default="medium", regex="^(low|medium|high)$")

class UserPreferencesCreate(UserPreferencesBase):
    pass

class UserPreferencesUpdate(UserPreferencesBase):
    pass

class UserPreferences(UserPreferencesBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 요청/응답 스키마
class MidiUploadResponse(BaseModel):
    midi_file: MidiFile
    message: str = "MIDI file uploaded successfully"

class MidiAnalysisRequest(BaseModel):
    analyze_chords: bool = True
    analyze_melody: bool = True
    analyze_rhythm: bool = True
    analyze_harmony: bool = True
    analyze_scale: bool = True

class MidiGenerationRequest(BaseModel):
    generation_type: str = Field(..., regex="^(improvisation|composition|variation)$")
    source_midi_id: Optional[int] = None
    prompt: Optional[str] = None
    style: Optional[str] = None
    duration: Optional[int] = Field(default=30, ge=10, le=300)
    complexity: Optional[str] = Field(default="medium", regex="^(low|medium|high)$")
    tempo: Optional[int] = Field(default=120, ge=60, le=200)
    key_signature: Optional[str] = None
    time_signature: Optional[str] = Field(default="4/4")
    instruments: Optional[List[str]] = None

class MidiGenerationResponse(BaseModel):
    generated_midi: GeneratedMidi
    download_url: str
    message: str = "MIDI generated successfully"

# 목록 응답 스키마
class MidiFilesListResponse(BaseModel):
    midi_files: List[MidiFile]
    total: int
    page: int
    size: int

class GeneratedMidiListResponse(BaseModel):
    generated_midi: List[GeneratedMidi]
    total: int
    page: int
    size: int

class MessageResponse(BaseModel):
    message: str