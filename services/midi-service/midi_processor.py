import mido
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import tempfile
import librosa
import numpy as np

class MidiProcessor:
    """MIDI 파일 처리 및 분석 클래스"""
    
    def __init__(self):
        self.supported_formats = ['.mid', '.midi']
    
    def validate_midi_file(self, file_path: str) -> bool:
        """MIDI 파일 유효성 검사"""
        try:
            midi_file = mido.MidiFile(file_path)
            return len(midi_file.tracks) > 0
        except Exception:
            return False
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """MIDI 파일에서 메타데이터 추출"""
        try:
            midi_file = mido.MidiFile(file_path)
            metadata = {
                'duration': midi_file.length,
                'track_count': len(midi_file.tracks),
                'ticks_per_beat': midi_file.ticks_per_beat,
                'time_signature': '4/4',  # 기본값
                'key_signature': 'C',     # 기본값
                'bpm': 120,               # 기본값
                'title': None,
                'artist': None,
                'instruments': []
            }
            
            # 각 트랙에서 메타 정보 추출
            for track in midi_file.tracks:
                for msg in track:
                    if msg.type == 'set_tempo':
                        # BPM 계산: BPM = 60,000,000 / microseconds_per_beat
                        bpm = 60000000 / msg.tempo
                        metadata['bpm'] = round(bpm, 2)
                    
                    elif msg.type == 'time_signature':
                        metadata['time_signature'] = f"{msg.numerator}/{2**msg.denominator}"
                    
                    elif msg.type == 'key_signature':
                        # 키 시그니처 매핑 (간단화)
                        key_map = {
                            0: 'C', 1: 'G', 2: 'D', 3: 'A', 4: 'E', 5: 'B', 6: 'F#',
                            7: 'C#', -1: 'F', -2: 'Bb', -3: 'Eb', -4: 'Ab', -5: 'Db',
                            -6: 'Gb', -7: 'Cb'
                        }
                        key = key_map.get(msg.key, 'C')
                        if msg.mode == 1:  # minor
                            key += 'm'
                        metadata['key_signature'] = key
                    
                    elif msg.type == 'text' and 'title' in msg.text.lower():
                        metadata['title'] = msg.text
                    
                    elif msg.type == 'text' and 'artist' in msg.text.lower():
                        metadata['artist'] = msg.text
                    
                    elif msg.type == 'program_change':
                        # 악기 정보 추출
                        instrument_name = self._get_instrument_name(msg.program)
                        if instrument_name not in metadata['instruments']:
                            metadata['instruments'].append(instrument_name)
            
            return metadata
            
        except Exception as e:
            raise ValueError(f"Failed to extract metadata: {str(e)}")
    
    def _get_instrument_name(self, program_number: int) -> str:
        """General MIDI 프로그램 번호를 악기 이름으로 변환"""
        # General MIDI 악기 매핑 (간단화된 버전)
        instrument_map = {
            0: "Acoustic Grand Piano", 1: "Bright Acoustic Piano", 2: "Electric Grand Piano",
            8: "Celesta", 9: "Glockenspiel", 10: "Music Box",
            24: "Acoustic Guitar (nylon)", 25: "Acoustic Guitar (steel)", 26: "Electric Guitar (jazz)",
            32: "Acoustic Bass", 33: "Electric Bass (finger)", 34: "Electric Bass (pick)",
            40: "Violin", 41: "Viola", 42: "Cello", 43: "Contrabass",
            56: "Trumpet", 57: "Trombone", 58: "Tuba",
            64: "Soprano Sax", 65: "Alto Sax", 66: "Tenor Sax", 67: "Baritone Sax",
            80: "Lead 1 (square)", 81: "Lead 2 (sawtooth)", 82: "Lead 3 (calliope)",
            128: "Drum Kit"  # 채널 9는 보통 드럼
        }
        return instrument_map.get(program_number, f"Program {program_number}")
    
    def analyze_harmony(self, file_path: str) -> Dict[str, Any]:
        """화성 분석"""
        try:
            midi_file = mido.MidiFile(file_path)
            
            # 시간별 노트 이벤트 수집
            notes_timeline = []
            current_time = 0
            
            for track in midi_file.tracks:
                track_time = 0
                active_notes = set()
                
                for msg in track:
                    track_time += msg.time
                    
                    if msg.type == 'note_on' and msg.velocity > 0:
                        active_notes.add(msg.note)
                        notes_timeline.append({
                            'time': track_time,
                            'type': 'note_on',
                            'note': msg.note,
                            'velocity': msg.velocity
                        })
                    
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        if msg.note in active_notes:
                            active_notes.remove(msg.note)
                        notes_timeline.append({
                            'time': track_time,
                            'type': 'note_off',
                            'note': msg.note
                        })
            
            # 코드 진행 분석 (간단화된 버전)
            chord_progression = self._analyze_chord_progression(notes_timeline)
            
            return {
                'chord_progression': chord_progression,
                'total_chords': len(chord_progression),
                'unique_chords': len(set(chord['chord_name'] for chord in chord_progression)),
                'analysis_method': 'note_overlap_detection'
            }
            
        except Exception as e:
            raise ValueError(f"Harmony analysis failed: {str(e)}")
    
    def _analyze_chord_progression(self, notes_timeline: List[Dict]) -> List[Dict[str, Any]]:
        """노트 타임라인에서 코드 진행 추출"""
        chords = []
        
        # 시간 윈도우별로 동시에 연주되는 노트들을 그룹화
        time_windows = {}
        
        for note_event in notes_timeline:
            # 500ms 단위로 그룹화 (간단화)
            window = int(note_event['time'] / 500) * 500
            
            if window not in time_windows:
                time_windows[window] = set()
            
            if note_event['type'] == 'note_on':
                time_windows[window].add(note_event['note'])
        
        # 각 윈도우에서 코드 식별
        for time, notes in time_windows.items():
            if len(notes) >= 3:  # 최소 3개 노트가 있어야 코드로 인식
                chord_name = self._identify_chord(list(notes))
                chords.append({
                    'time': time,
                    'chord_name': chord_name,
                    'notes': sorted(list(notes)),
                    'duration': 500  # 간단화
                })
        
        return chords
    
    def _identify_chord(self, notes: List[int]) -> str:
        """노트 집합에서 코드 이름 식별 (간단화된 버전)"""
        # 노트를 0-11 범위로 정규화 (옥타브 무시)
        chord_notes = sorted(set(note % 12 for note in notes))
        
        # 기본적인 코드 패턴 매칭
        chord_patterns = {
            (0, 4, 7): "C",
            (2, 6, 9): "D",
            (4, 8, 11): "E",
            (5, 9, 0): "F",
            (7, 11, 2): "G",
            (9, 1, 4): "A",
            (11, 3, 6): "B",
            (0, 3, 7): "Cm",
            (2, 5, 9): "Dm",
            (4, 7, 11): "Em",
            (5, 8, 0): "Fm",
            (7, 10, 2): "Gm",
            (9, 0, 4): "Am",
            (11, 2, 6): "Bm"
        }
        
        # 가장 가까운 패턴 찾기
        root_note = chord_notes[0]
        normalized_pattern = tuple((note - root_note) % 12 for note in chord_notes[:3])
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        root_name = note_names[root_note]
        
        # 패턴 매칭
        for pattern, chord_type in chord_patterns.items():
            if normalized_pattern == pattern:
                if chord_type.endswith('m'):
                    return f"{root_name}m"
                else:
                    return root_name
        
        return f"{root_name}?"  # 알 수 없는 코드
    
    def generate_improvisation(self, 
                             source_file_path: str,
                             style: str = "jazz",
                             complexity: str = "medium",
                             duration: int = 30) -> str:
        """즉흥연주 MIDI 생성 (간단화된 버전)"""
        
        try:
            # 원본 MIDI 분석
            source_midi = mido.MidiFile(source_file_path)
            metadata = self.extract_metadata(source_file_path)
            
            # 새로운 MIDI 파일 생성
            new_midi = mido.MidiFile(ticks_per_beat=source_midi.ticks_per_beat)
            track = mido.MidiTrack()
            new_midi.tracks.append(track)
            
            # 템포 설정
            tempo = int(60000000 / metadata['bpm'])
            track.append(mido.MetaMessage('set_tempo', tempo=tempo))
            
            # 간단한 즉흥연주 생성 (기본 스케일 기반)
            scale_notes = self._get_scale_notes(metadata.get('key_signature', 'C'), style)
            
            # 리듬 패턴 생성
            beats_per_measure = 4
            ticks_per_beat = source_midi.ticks_per_beat
            total_ticks = duration * metadata['bpm'] * ticks_per_beat // 60
            
            current_tick = 0
            while current_tick < total_ticks:
                # 랜덤하게 노트 선택 및 연주
                note = np.random.choice(scale_notes)
                velocity = np.random.randint(60, 100)
                note_duration = ticks_per_beat // 2  # 8분음표
                
                # Note On
                track.append(mido.Message('note_on', 
                                        channel=0, 
                                        note=note, 
                                        velocity=velocity, 
                                        time=0))
                
                # Note Off
                track.append(mido.Message('note_off', 
                                        channel=0, 
                                        note=note, 
                                        velocity=0, 
                                        time=note_duration))
                
                current_tick += note_duration
                
                # 간헐적 휴식
                if np.random.random() > 0.8:
                    rest_duration = ticks_per_beat // 4
                    track.append(mido.Message('note_on', 
                                            channel=0, 
                                            note=60, 
                                            velocity=0, 
                                            time=rest_duration))
                    current_tick += rest_duration
            
            # 임시 파일로 저장
            temp_file = tempfile.NamedTemporaryFile(suffix='.mid', delete=False)
            new_midi.save(temp_file.name)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            raise ValueError(f"Improvisation generation failed: {str(e)}")
    
    def _get_scale_notes(self, key: str, style: str) -> List[int]:
        """키와 스타일에 따른 스케일 노트 반환"""
        # C 메이저 스케일 기본 (간단화)
        major_scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C4-C5
        
        if style == "jazz":
            # 재즈 스케일 (블루스 노트 추가)
            return major_scale + [63, 66, 70]  # Eb, F#, Bb 추가
        elif style == "blues":
            # 블루스 스케일
            return [60, 63, 65, 66, 67, 70, 72]
        else:
            # 기본 메이저 스케일
            return major_scale