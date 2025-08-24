#!/usr/bin/env python3
"""
RAG 기반 실시간 즉흥 연주 시스템
MIDI 코드 진행을 분석하고 개인화된 솔로 라인을 생성합니다.
"""

import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import deque
import time
from dataclasses import dataclass
import sqlite3
import mido

@dataclass
class ChordInfo:
    """코드 정보 데이터 클래스"""
    root: int           # 근음 (MIDI 노트 번호)
    chord_type: str     # 코드 타입 (major, minor, dim, aug 등)
    notes: List[int]    # 코드 구성음
    timestamp: float    # 연주 시각
    duration: float     # 지속 시간

@dataclass
class SoloNote:
    """솔로 노트 정보 데이터 클래스"""
    note: int          # MIDI 노트 번호
    velocity: int      # 벨로시티
    start_time: float  # 시작 시간 (박자 기준)
    duration: float    # 길이 (박자 기준)
    probability: float # AI 모델 확신도

class ChordAnalyzer:
    """실시간 코드 분석기"""
    
    def __init__(self):
        self.current_notes = set()
        self.chord_history = deque(maxlen=8)  # 최근 8개 코드 기억
        
        # 코드 패턴 정의
        self.chord_patterns = {
            # Major 계열
            (0, 4, 7): "major",
            (0, 4, 7, 11): "major7",
            (0, 4, 7, 10): "dominant7",
            (0, 4, 7, 9): "major6",
            (0, 4, 7, 9, 11): "major9",
            
            # Minor 계열
            (0, 3, 7): "minor",
            (0, 3, 7, 10): "minor7",
            (0, 3, 7, 11): "minorMaj7",
            (0, 3, 7, 9): "minor6",
            (0, 3, 7, 9, 10): "minor9",
            
            # Diminished/Augmented
            (0, 3, 6): "diminished",
            (0, 3, 6, 9): "diminished7",
            (0, 4, 8): "augmented",
            
            # Sus 계열
            (0, 5, 7): "sus4",
            (0, 2, 7): "sus2",
            
            # 기타
            (0, 5): "power_chord",
            (0, 7): "fifth",
        }
    
    def add_note(self, note: int):
        """노트 추가"""
        self.current_notes.add(note % 12)  # 옥타브 무시
        self._analyze_chord()
    
    def remove_note(self, note: int):
        """노트 제거"""
        self.current_notes.discard(note % 12)
        if self.current_notes:
            self._analyze_chord()
    
    def _analyze_chord(self):
        """현재 노트들로 코드 분석"""
        if len(self.current_notes) < 2:
            return None
        
        # 모든 가능한 루트로 코드 분석 시도
        for root in self.current_notes:
            intervals = tuple(sorted((note - root) % 12 for note in self.current_notes))
            
            if intervals in self.chord_patterns:
                chord_type = self.chord_patterns[intervals]
                chord_info = ChordInfo(
                    root=root,
                    chord_type=chord_type,
                    notes=list(self.current_notes),
                    timestamp=time.time(),
                    duration=0.0
                )
                
                # 코드 기록에 추가
                if not self.chord_history or self.chord_history[-1].root != root or self.chord_history[-1].chord_type != chord_type:
                    self.chord_history.append(chord_info)
                    print(f"🎼 코드 감지: {self._note_name(root)} {chord_type} {intervals}")
                
                return chord_info
        
        return None
    
    def _note_name(self, note: int) -> str:
        """MIDI 노트를 음명으로 변환"""
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return names[note % 12]
    
    def get_chord_progression(self) -> List[ChordInfo]:
        """현재 코드 진행 반환"""
        return list(self.chord_history)

class SoloPatternDatabase:
    """솔로 패턴 데이터베이스 (RAG 시스템)"""
    
    def __init__(self, db_path: str = "solo_patterns.db"):
        self.db_path = db_path
        self._init_database()
        self._populate_sample_data()
    
    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 솔로 패턴 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solo_patterns (
                id INTEGER PRIMARY KEY,
                chord_progression TEXT,
                solo_pattern TEXT,
                style TEXT,
                difficulty INTEGER,
                usage_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0
            )
        ''')
        
        # 사용자 선호도 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY,
                pattern_id INTEGER,
                preference_score REAL,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pattern_id) REFERENCES solo_patterns (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _populate_sample_data(self):
        """샘플 솔로 패턴 데이터 추가"""
        sample_patterns = [
            # C Major 패턴들
            {
                'chord_progression': 'C-Am-F-G',
                'solo_pattern': '[60,62,64,65,67,65,64,62]',  # C major scale run
                'style': 'jazz',
                'difficulty': 2
            },
            {
                'chord_progression': 'C-Am-F-G',
                'solo_pattern': '[72,69,67,65,64,62,60]',     # 하행 arpeggios
                'style': 'classical',
                'difficulty': 1
            },
            {
                'chord_progression': 'C-F-G-C',
                'solo_pattern': '[60,64,67,69,67,64,65,62]',  # 펜타토닉 변형
                'style': 'blues',
                'difficulty': 2
            },
            
            # Jazz 진행 패턴들
            {
                'chord_progression': 'Dm7-G7-Cmaj7',
                'solo_pattern': '[62,65,67,69,71,69,67,65,64,62,60]',
                'style': 'jazz',
                'difficulty': 3
            },
            {
                'chord_progression': 'Am7-D7-Gmaj7',
                'solo_pattern': '[69,67,66,64,62,64,66,67,69]',
                'style': 'jazz',
                'difficulty': 3
            },
            
            # 블루스 패턴들
            {
                'chord_progression': 'C7-F7-G7',
                'solo_pattern': '[60,63,64,66,67,66,64,63,60]',  # 블루스 스케일
                'style': 'blues',
                'difficulty': 2
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pattern in sample_patterns:
            cursor.execute('''
                INSERT OR IGNORE INTO solo_patterns 
                (chord_progression, solo_pattern, style, difficulty)
                VALUES (?, ?, ?, ?)
            ''', (
                pattern['chord_progression'],
                pattern['solo_pattern'],
                pattern['style'],
                pattern['difficulty']
            ))
        
        conn.commit()
        conn.close()
    
    def search_patterns(self, chord_progression: List[ChordInfo], style: str = None) -> List[Dict]:
        """코드 진행에 맞는 솔로 패턴 검색"""
        # 코드 진행을 문자열로 변환
        prog_str = self._chord_progression_to_string(chord_progression)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 유사한 패턴 검색 (부분 매칭 포함)
        if style:
            cursor.execute('''
                SELECT * FROM solo_patterns 
                WHERE chord_progression LIKE ? AND style = ?
                ORDER BY usage_count DESC, rating DESC
                LIMIT 10
            ''', (f'%{prog_str}%', style))
        else:
            cursor.execute('''
                SELECT * FROM solo_patterns 
                WHERE chord_progression LIKE ?
                ORDER BY usage_count DESC, rating DESC
                LIMIT 10
            ''', (f'%{prog_str}%',))
        
        results = cursor.fetchall()
        conn.close()
        
        # 딕셔너리 형태로 변환
        patterns = []
        for row in results:
            patterns.append({
                'id': row[0],
                'chord_progression': row[1],
                'solo_pattern': json.loads(row[2]),
                'style': row[3],
                'difficulty': row[4],
                'usage_count': row[5],
                'rating': row[6]
            })
        
        return patterns
    
    def _chord_progression_to_string(self, chords: List[ChordInfo]) -> str:
        """코드 진행을 문자열로 변환"""
        chord_names = []
        for chord in chords:
            root_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][chord.root]
            chord_names.append(f"{root_name}{chord.chord_type}")
        
        return '-'.join(chord_names)

class ImprovisationEngine:
    """개인화된 즉흥 연주 생성 엔진"""
    
    def __init__(self):
        self.chord_analyzer = ChordAnalyzer()
        self.pattern_db = SoloPatternDatabase()
        self.user_style_preferences = {
            'jazz': 0.7,
            'blues': 0.8,
            'classical': 0.5,
            'rock': 0.6
        }
        self.current_solo = deque(maxlen=16)  # 현재 생성 중인 솔로
        
    def process_midi_input(self, note: int, velocity: int, is_note_on: bool):
        """MIDI 입력 처리"""
        if is_note_on and velocity > 0:
            self.chord_analyzer.add_note(note)
        else:
            self.chord_analyzer.remove_note(note)
        
        # 새로운 코드가 감지되면 솔로 생성
        chord_progression = self.chord_analyzer.get_chord_progression()
        if len(chord_progression) >= 2:
            solo_notes = self.generate_solo(chord_progression)
            if solo_notes:
                print(f"🎵 솔로 생성: {[n.note for n in solo_notes]}")
                return solo_notes
        
        return []
    
    def generate_solo(self, chord_progression: List[ChordInfo]) -> List[SoloNote]:
        """개인화된 솔로 라인 생성"""
        # 사용자 선호도 기반 스타일 선택
        preferred_style = max(self.user_style_preferences.items(), key=lambda x: x[1])[0]
        
        # RAG: 유사한 패턴 검색
        patterns = self.pattern_db.search_patterns(chord_progression, preferred_style)
        
        if not patterns:
            # 기본 패턴으로 폴백
            return self._generate_basic_solo(chord_progression[-1])
        
        # 최적 패턴 선택 (사용자 선호도 + 코드 매칭도)
        best_pattern = self._select_best_pattern(patterns, chord_progression)
        
        # 패턴을 SoloNote 객체로 변환
        solo_notes = []
        pattern_notes = best_pattern['solo_pattern']
        
        for i, note in enumerate(pattern_notes):
            solo_note = SoloNote(
                note=note,
                velocity=80 + np.random.randint(-20, 21),  # 60-100 랜덤
                start_time=i * 0.25,  # 16분음표 간격
                duration=0.25,
                probability=0.8
            )
            solo_notes.append(solo_note)
        
        # 패턴 사용 횟수 업데이트
        self._update_pattern_usage(best_pattern['id'])
        
        return solo_notes
    
    def _select_best_pattern(self, patterns: List[Dict], chord_progression: List[ChordInfo]) -> Dict:
        """최적 패턴 선택 (개인화 알고리즘)"""
        scored_patterns = []
        
        for pattern in patterns:
            score = 0.0
            
            # 스타일 선호도 점수
            style_preference = self.user_style_preferences.get(pattern['style'], 0.5)
            score += style_preference * 0.4
            
            # 사용 빈도 점수 (많이 사용된 패턴 선호)
            usage_score = min(pattern['usage_count'] / 10.0, 1.0)
            score += usage_score * 0.3
            
            # 평점 점수
            rating_score = pattern['rating'] / 5.0
            score += rating_score * 0.2
            
            # 난이도 적합성 (중간 난이도 선호)
            difficulty_score = 1.0 - abs(pattern['difficulty'] - 2.5) / 2.5
            score += difficulty_score * 0.1
            
            scored_patterns.append((pattern, score))
        
        # 점수 기반 정렬
        scored_patterns.sort(key=lambda x: x[1], reverse=True)
        
        return scored_patterns[0][0]
    
    def _generate_basic_solo(self, current_chord: ChordInfo) -> List[SoloNote]:
        """기본 솔로 패턴 생성 (폴백)"""
        # 코드 구성음 기반 간단한 아르페지오
        chord_notes = sorted(current_chord.notes)
        octave_notes = chord_notes + [note + 12 for note in chord_notes]
        
        solo_notes = []
        for i, note in enumerate(octave_notes[:8]):
            solo_note = SoloNote(
                note=note + 60,  # 중간 옥타브로 이동
                velocity=70,
                start_time=i * 0.125,  # 32분음표
                duration=0.125,
                probability=0.6
            )
            solo_notes.append(solo_note)
        
        return solo_notes
    
    def _update_pattern_usage(self, pattern_id: int):
        """패턴 사용 횟수 업데이트"""
        conn = sqlite3.connect(self.pattern_db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE solo_patterns 
            SET usage_count = usage_count + 1 
            WHERE id = ?
        ''', (pattern_id,))
        
        conn.commit()
        conn.close()

class MidiOutputManager:
    """MIDI 출력 관리자 (FL Studio 연동)"""
    
    def __init__(self, output_port_name: str = None):
        self.output_port = None
        self.connect_output(output_port_name)
    
    def connect_output(self, port_name: str = None):
        """MIDI 출력 포트 연결"""
        try:
            available_ports = mido.get_output_names()
            
            if port_name and port_name in available_ports:
                self.output_port = mido.open_output(port_name)
                print(f"✅ MIDI 출력 연결: {port_name}")
            elif available_ports:
                # loopMIDI나 FL Studio 포트 우선 선택
                for port in available_ports:
                    if "loopMIDI" in port or "FL Studio" in port:
                        self.output_port = mido.open_output(port)
                        print(f"✅ MIDI 출력 자동 선택: {port}")
                        break
                else:
                    # 첫 번째 포트 사용
                    self.output_port = mido.open_output(available_ports[0])
                    print(f"✅ MIDI 출력 기본 선택: {available_ports[0]}")
            else:
                print("❌ MIDI 출력 포트를 찾을 수 없습니다.")
        
        except Exception as e:
            print(f"❌ MIDI 출력 연결 실패: {e}")
    
    def send_solo(self, solo_notes: List[SoloNote], channel: int = 0):
        """솔로 노트들을 FL Studio로 전송"""
        if not self.output_port:
            print("❌ MIDI 출력 포트가 연결되지 않았습니다.")
            return
        
        print(f"🎵 솔로 전송 시작: {len(solo_notes)}개 노트")
        
        # 솔로 노트 전송
        for note in solo_notes:
            try:
                # Note On
                msg_on = mido.Message('note_on', 
                                    channel=channel, 
                                    note=note.note, 
                                    velocity=note.velocity)
                self.output_port.send(msg_on)
                
                # 노트 지속 시간 대기
                time.sleep(note.duration)
                
                # Note Off
                msg_off = mido.Message('note_off', 
                                     channel=channel, 
                                     note=note.note, 
                                     velocity=0)
                self.output_port.send(msg_off)
                
                print(f"  🎵 전송: Note {note.note} (V:{note.velocity})")
                
            except Exception as e:
                print(f"❌ 노트 전송 실패: {e}")
    
    def close(self):
        """MIDI 출력 포트 닫기"""
        if self.output_port:
            self.output_port.close()
            print("👋 MIDI 출력 포트 닫힘")

# 테스트 함수
def test_improvisation_system():
    """즉흥 연주 시스템 테스트"""
    print("🎹 RAG 기반 즉흥 연주 시스템 테스트")
    print("=" * 60)
    
    # 시스템 초기화
    engine = ImprovisationEngine()
    output_manager = MidiOutputManager()
    
    # 테스트 코드 진행: C - Am - F - G
    test_chords = [
        (60, 64, 67),    # C major
        (57, 60, 64),    # A minor
        (53, 57, 60),    # F major
        (55, 59, 62)     # G major
    ]
    
    print("🎼 테스트 코드 진행 입력...")
    
    for i, chord_notes in enumerate(test_chords):
        print(f"\n코드 {i+1}: {chord_notes}")
        
        # 코드 노트들 입력
        for note in chord_notes:
            engine.process_midi_input(note, 80, True)
        
        time.sleep(1)  # 1초 대기
        
        # 코드 노트들 해제
        for note in chord_notes:
            engine.process_midi_input(note, 0, False)
    
    print(f"\n📊 시스템 상태:")
    progression = engine.chord_analyzer.get_chord_progression()
    print(f"  감지된 코드 수: {len(progression)}")
    
    for chord in progression:
        print(f"  - {chord.root} {chord.chord_type}: {chord.notes}")
    
    output_manager.close()

if __name__ == "__main__":
    test_improvisation_system()