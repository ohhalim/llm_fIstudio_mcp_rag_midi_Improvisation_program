#!/usr/bin/env python3
"""
실시간 MIDI 즉흥 연주 시스템
MIDI 입력을 실시간으로 분석하고 RAG 기반 솔로 라인을 생성합니다.
"""

import mido
import time
import threading
from datetime import datetime
from collections import deque, Counter
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import json

@dataclass
class ChordInfo:
    """코드 정보"""
    root: int           # 근음 (0-11, C=0)
    chord_type: str     # major, minor, dim, aug 등
    notes: List[int]    # 구성음들 (0-11)
    confidence: float   # 분석 확신도
    timestamp: float    # 감지 시간

@dataclass
class SoloPattern:
    """솔로 패턴"""
    notes: List[int]    # MIDI 노트 번호들
    durations: List[float] # 각 노트의 길이
    style: str         # jazz, blues, rock 등
    difficulty: int    # 1-5 난이도

class ChordAnalyzer:
    """실시간 코드 분석기"""
    
    def __init__(self):
        self.current_notes = set()
        self.chord_buffer = deque(maxlen=50)  # 최근 50개 노트 기억
        self.last_chord = None
        
        # 코드 패턴 정의 (반음 간격)
        self.chord_patterns = {
            frozenset([0, 4, 7]): "major",
            frozenset([0, 3, 7]): "minor", 
            frozenset([0, 4, 7, 11]): "maj7",
            frozenset([0, 4, 7, 10]): "7",
            frozenset([0, 3, 7, 10]): "m7",
            frozenset([0, 3, 6]): "dim",
            frozenset([0, 4, 8]): "aug",
            frozenset([0, 5, 7]): "sus4",
            frozenset([0, 2, 7]): "sus2",
            frozenset([0, 7]): "5",
        }
    
    def add_note(self, note: int, velocity: int, timestamp: float):
        """노트 추가"""
        note_class = note % 12  # 옥타브 제거
        self.current_notes.add(note_class)
        self.chord_buffer.append((note_class, velocity, timestamp))
        
        # 코드 분석 시도
        chord = self._analyze_current_chord()
        if chord and chord != self.last_chord:
            self.last_chord = chord
            print(f"🎼 코드 감지: {self._chord_to_string(chord)}")
            return chord
        return None
    
    def remove_note(self, note: int):
        """노트 제거"""
        note_class = note % 12
        self.current_notes.discard(note_class)
        
        # 여전히 남은 노트들로 코드 재분석
        if len(self.current_notes) >= 2:
            chord = self._analyze_current_chord()
            if chord != self.last_chord:
                self.last_chord = chord
                if chord:
                    print(f"🎼 코드 변경: {self._chord_to_string(chord)}")
                return chord
        return None
    
    def _analyze_current_chord(self) -> Optional[ChordInfo]:
        """현재 노트들로 코드 분석"""
        if len(self.current_notes) < 2:
            return None
        
        # 모든 가능한 루트로 시도
        best_chord = None
        best_confidence = 0.0
        
        for root in self.current_notes:
            # 루트 기준으로 인터벌 계산
            intervals = frozenset((note - root) % 12 for note in self.current_notes)
            
            if intervals in self.chord_patterns:
                chord_type = self.chord_patterns[intervals]
                confidence = len(intervals) / 4.0  # 더 많은 노트 = 더 높은 확신도
                
                if confidence > best_confidence:
                    best_chord = ChordInfo(
                        root=root,
                        chord_type=chord_type,
                        notes=sorted(list(self.current_notes)),
                        confidence=confidence,
                        timestamp=time.time()
                    )
                    best_confidence = confidence
        
        return best_chord
    
    def _chord_to_string(self, chord: ChordInfo) -> str:
        """코드를 문자열로 변환"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return f"{note_names[chord.root]}{chord.chord_type}"
    
    def get_recent_progression(self, count: int = 4) -> List[str]:
        """최근 코드 진행 반환"""
        # TODO: 코드 히스토리 구현
        return []

class SoloGenerator:
    """RAG 기반 솔로 생성기"""
    
    def __init__(self):
        self.solo_database = self._load_solo_patterns()
        self.user_preferences = {
            'jazz': 0.8,
            'blues': 0.9,
            'rock': 0.6,
            'classical': 0.4
        }
    
    def _load_solo_patterns(self) -> Dict[str, List[SoloPattern]]:
        """솔로 패턴 데이터베이스 로드"""
        patterns = {
            # C major 관련 패턴들
            'C_major': [
                SoloPattern([60, 62, 64, 65, 67, 65, 64, 62], [0.25]*8, 'jazz', 2),
                SoloPattern([72, 69, 67, 65, 64, 62, 60], [0.25]*7, 'classical', 1),
                SoloPattern([60, 63, 64, 67, 65, 62, 60], [0.25]*7, 'blues', 2),
            ],
            
            # A minor 관련 패턴들  
            'A_minor': [
                SoloPattern([57, 60, 62, 64, 65, 64, 62, 60], [0.25]*8, 'jazz', 2),
                SoloPattern([69, 67, 65, 64, 62, 60, 57], [0.25]*7, 'classical', 1),
            ],
            
            # F major 관련 패턴들
            'F_major': [
                SoloPattern([53, 55, 57, 58, 60, 62, 64, 65], [0.25]*8, 'jazz', 2),
                SoloPattern([65, 64, 62, 60, 58, 57, 55, 53], [0.25]*8, 'classical', 1),
            ],
            
            # G major 관련 패턴들
            'G_major': [
                SoloPattern([55, 57, 59, 60, 62, 64, 66, 67], [0.25]*8, 'jazz', 2),
                SoloPattern([67, 66, 64, 62, 60, 59, 57, 55], [0.25]*8, 'classical', 1),
            ],
            
            # 7th 코드 패턴들
            'C_7': [
                SoloPattern([60, 64, 67, 70, 72, 70, 67, 64], [0.25]*8, 'jazz', 3),
                SoloPattern([60, 63, 65, 67, 70, 67, 65, 63], [0.25]*8, 'blues', 3),
            ],
        }
        
        return patterns
    
    def generate_solo(self, chord: ChordInfo, style_preference: str = 'jazz') -> Optional[SoloPattern]:
        """코드에 맞는 솔로 생성"""
        chord_key = f"{self._chord_to_string(chord)}"
        
        # 정확히 일치하는 패턴 찾기
        if chord_key in self.solo_database:
            patterns = self.solo_database[chord_key]
            
            # 스타일 선호도에 따라 패턴 선택
            best_pattern = None
            best_score = 0.0
            
            for pattern in patterns:
                score = self.user_preferences.get(pattern.style, 0.5)
                if pattern.style == style_preference:
                    score += 0.3  # 선호 스타일 보너스
                
                if score > best_score:
                    best_pattern = pattern
                    best_score = score
            
            return best_pattern
        
        # 일치하는 패턴이 없으면 기본 아르페지오 생성
        return self._generate_basic_arpeggio(chord)
    
    def _generate_basic_arpeggio(self, chord: ChordInfo) -> SoloPattern:
        """기본 아르페지오 패턴 생성"""
        # 코드 구성음을 중음역대로 변환
        base_octave = 60  # C4
        chord_notes = [note + base_octave for note in chord.notes]
        
        # 상행 + 하행 아르페지오
        notes = chord_notes + chord_notes[::-1]
        durations = [0.25] * len(notes)
        
        return SoloPattern(notes, durations, 'basic', 1)
    
    def _chord_to_string(self, chord: ChordInfo) -> str:
        """코드를 문자열로 변환 (데이터베이스 키용)"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return f"{note_names[chord.root]}_{chord.chord_type}"

class MidiImprovisationSystem:
    """실시간 MIDI 즉흥 연주 시스템"""
    
    def __init__(self, input_port_name: str = None, output_port_name: str = None):
        self.chord_analyzer = ChordAnalyzer()
        self.solo_generator = SoloGenerator()
        
        self.input_port = None
        self.output_port = None
        self.running = False
        
        self.connect_ports(input_port_name, output_port_name)
    
    def connect_ports(self, input_port_name: str = None, output_port_name: str = None):
        """MIDI 포트 연결"""
        # 입력 포트 연결
        input_ports = mido.get_input_names()
        if input_port_name and input_port_name in input_ports:
            self.input_port = input_port_name
        else:
            # Keystation 자동 선택
            for port in input_ports:
                if "Keystation" in port:
                    self.input_port = port
                    break
        
        # 출력 포트 연결  
        output_ports = mido.get_output_names()
        if output_port_name and output_port_name in output_ports:
            self.output_port = output_port_name
        else:
            # FL Studio/loopMIDI 자동 선택
            for port in output_ports:
                if "loopMIDI" in port or "FL Studio" in port:
                    self.output_port = port
                    break
        
        print(f"🎹 입력: {self.input_port}")
        print(f"🔊 출력: {self.output_port}")
    
    def start_listening(self):
        """실시간 MIDI 리스닝 시작"""
        if not self.input_port:
            print("❌ MIDI 입력 포트가 없습니다.")
            return
        
        try:
            with mido.open_input(self.input_port) as inport:
                print("🎵 실시간 즉흥 연주 시스템 시작!")
                print("=" * 50)
                print("코드를 연주하면 자동으로 솔로를 생성합니다...")
                print("=" * 50)
                
                self.running = True
                
                for message in inport:
                    if not self.running:
                        break
                    
                    self.process_midi_message(message)
        
        except KeyboardInterrupt:
            print("\n🛑 시스템 종료")
        except Exception as e:
            print(f"❌ 오류: {e}")
        finally:
            self.running = False
    
    def process_midi_message(self, message):
        """MIDI 메시지 처리"""
        if message.type == 'note_on' and message.velocity > 0:
            # 노트 추가
            chord = self.chord_analyzer.add_note(message.note, message.velocity, time.time())
            
            # 새로운 코드가 감지되면 솔로 생성
            if chord:
                self.generate_and_play_solo(chord)
        
        elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
            # 노트 제거
            self.chord_analyzer.remove_note(message.note)
    
    def generate_and_play_solo(self, chord: ChordInfo):
        """솔로 생성 및 연주"""
        print(f"🎼 솔로 생성 중... ({self.chord_analyzer._chord_to_string(chord)})")
        
        # 솔로 패턴 생성
        solo_pattern = self.solo_generator.generate_solo(chord, 'jazz')
        
        if not solo_pattern:
            print("❌ 솔로 생성 실패")
            return
        
        print(f"🎵 솔로 연주: {len(solo_pattern.notes)}개 노트 ({solo_pattern.style} 스타일)")
        
        # 별도 스레드에서 솔로 연주 (메인 루프 블록하지 않음)
        if self.output_port:
            solo_thread = threading.Thread(
                target=self._play_solo_pattern, 
                args=(solo_pattern,),
                daemon=True
            )
            solo_thread.start()
        else:
            # 출력 포트가 없으면 콘솔에만 표시
            self._display_solo_pattern(solo_pattern)
    
    def _play_solo_pattern(self, pattern: SoloPattern):
        """솔로 패턴을 MIDI로 연주"""
        if not self.output_port:
            return
        
        try:
            with mido.open_output(self.output_port) as outport:
                for note, duration in zip(pattern.notes, pattern.durations):
                    # Note On
                    outport.send(mido.Message('note_on', note=note, velocity=80))
                    
                    # 지속 시간만큼 대기
                    time.sleep(duration * 0.5)  # 템포 조절 (0.5 = 120 BPM 기준)
                    
                    # Note Off
                    outport.send(mido.Message('note_off', note=note, velocity=0))
                    
                    # 짧은 간격
                    time.sleep(duration * 0.1)
        
        except Exception as e:
            print(f"❌ 솔로 연주 실패: {e}")
    
    def _display_solo_pattern(self, pattern: SoloPattern):
        """솔로 패턴을 콘솔에 표시"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        print("🎵 생성된 솔로:")
        for i, (note, duration) in enumerate(zip(pattern.notes, pattern.durations)):
            octave = note // 12 - 1
            note_name = note_names[note % 12]
            print(f"  {i+1}. {note_name}{octave} (길이: {duration})")
    
    def stop(self):
        """시스템 정지"""
        self.running = False

def main():
    """메인 함수"""
    print("🎹 실시간 MIDI 즉흥 연주 시스템")
    print("=" * 50)
    
    # MIDI 포트 확인
    print("📋 사용 가능한 MIDI 포트:")
    print("입력:", mido.get_input_names())
    print("출력:", mido.get_output_names())
    print()
    
    # 시스템 시작
    system = MidiImprovisationSystem()
    
    try:
        system.start_listening()
    except KeyboardInterrupt:
        print("\n👋 프로그램 종료")
    finally:
        system.stop()

if __name__ == "__main__":
    main()