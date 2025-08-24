#!/usr/bin/env python3
"""
실시간 코드 인식 테스트
사용자가 연주하는 코드를 실시간으로 분석하고 표시합니다.
"""

import mido
import time
from datetime import datetime
from collections import defaultdict

class RealtimeChordRecognizer:
    """실시간 코드 인식기"""
    
    def __init__(self):
        self.current_notes = set()
        self.note_start_times = {}
        
        # 코드 패턴 정의 (루트에서의 반음 간격)
        self.chord_patterns = {
            frozenset([0, 4, 7]): "major",
            frozenset([0, 3, 7]): "minor",
            frozenset([0, 4, 7, 11]): "maj7",
            frozenset([0, 4, 7, 10]): "dom7", 
            frozenset([0, 3, 7, 10]): "min7",
            frozenset([0, 3, 7, 11]): "minMaj7",
            frozenset([0, 4, 7, 9]): "6",
            frozenset([0, 3, 7, 9]): "min6",
            frozenset([0, 4, 7, 9, 11]): "maj9",
            frozenset([0, 3, 7, 9, 10]): "min9",
            frozenset([0, 4, 7, 10, 14]): "9",
            frozenset([0, 3, 6]): "dim",
            frozenset([0, 3, 6, 9]): "dim7",
            frozenset([0, 4, 8]): "aug",
            frozenset([0, 5, 7]): "sus4",
            frozenset([0, 2, 7]): "sus2",
            frozenset([0, 5, 7, 10]): "7sus4",
            frozenset([0, 7]): "5 (power chord)",
            frozenset([0, 4]): "major (no 5th)",
            frozenset([0, 3]): "minor (no 5th)",
        }
        
        # 음명 변환
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        self.last_analyzed_chord = None
        self.chord_confidence_threshold = 0.3  # 0.3초 이상 지속되면 코드로 인정
    
    def add_note(self, note: int, velocity: int, timestamp: float):
        """노트 추가 및 코드 분석"""
        note_class = note % 12
        self.current_notes.add(note_class)
        self.note_start_times[note_class] = timestamp
        
        # 실시간 코드 분석
        self._analyze_chord()
    
    def remove_note(self, note: int, timestamp: float):
        """노트 제거"""
        note_class = note % 12
        self.current_notes.discard(note_class)
        self.note_start_times.pop(note_class, None)
        
        # 남은 노트들로 재분석
        if len(self.current_notes) >= 2:
            self._analyze_chord()
        elif len(self.current_notes) < 2:
            print("🎵 [코드 해제]")
    
    def _analyze_chord(self):
        """현재 노트들을 코드로 분석"""
        if len(self.current_notes) < 2:
            return
        
        current_time = time.time()
        
        # 충분히 오래 지속된 노트들만 고려
        stable_notes = set()
        for note in self.current_notes:
            if current_time - self.note_start_times.get(note, current_time) >= self.chord_confidence_threshold:
                stable_notes.add(note)
        
        if len(stable_notes) < 2:
            return
        
        # 가능한 모든 루트로 코드 분석 시도
        best_chord = None
        best_score = 0
        
        for root in stable_notes:
            intervals = frozenset((note - root) % 12 for note in stable_notes)
            
            if intervals in self.chord_patterns:
                chord_type = self.chord_patterns[intervals]
                # 점수 계산: 더 많은 노트 = 더 높은 점수
                score = len(stable_notes)
                
                if score > best_score:
                    best_chord = (root, chord_type, sorted(list(stable_notes)))
                    best_score = score
        
        # 새로운 코드가 감지되었거나 변경되었으면 출력
        if best_chord and best_chord != self.last_analyzed_chord:
            root, chord_type, notes = best_chord
            chord_name = f"{self.note_names[root]} {chord_type}"
            note_list = [self.note_names[note] for note in notes]
            
            print(f"🎼 [{datetime.now().strftime('%H:%M:%S')}] 코드: {chord_name}")
            print(f"   구성음: {' + '.join(note_list)} ({len(notes)}음)")
            print(f"   확신도: {len(stable_notes)}/4 ⭐" + "⭐" * min(len(stable_notes)-1, 3))
            
            self.last_analyzed_chord = best_chord
            
            # 코드 진행 추천
            self._suggest_next_chords(root, chord_type)
    
    def _suggest_next_chords(self, root: int, chord_type: str):
        """다음 코드 진행 추천"""
        suggestions = []
        
        # 기본적인 코드 진행 패턴
        if "major" in chord_type:
            # I-vi-IV-V 진행
            suggestions.extend([
                self.note_names[(root + 9) % 12] + " minor",  # vi
                self.note_names[(root + 5) % 12] + " major",  # IV  
                self.note_names[(root + 7) % 12] + " dom7",   # V7
            ])
        elif "minor" in chord_type:
            # i-VII-VI-VII 또는 i-iv-V7-i
            suggestions.extend([
                self.note_names[(root + 10) % 12] + " major", # VII
                self.note_names[(root + 8) % 12] + " major",  # VI
                self.note_names[(root + 5) % 12] + " minor",  # iv
                self.note_names[(root + 7) % 12] + " dom7",   # V7
            ])
        elif "dom7" in chord_type or "7" in chord_type:
            # V7-I 해결
            suggestions.extend([
                self.note_names[(root + 5) % 12] + " major",  # I
                self.note_names[(root + 5) % 12] + " minor",  # i (minor key)
            ])
        
        if suggestions:
            print(f"   💡 추천 다음 코드: {', '.join(suggestions[:3])}")
        print()

def main():
    """실시간 코드 인식 시작"""
    print("🎹 실시간 코드 인식 시스템")
    print("=" * 60)
    
    # MIDI 포트 확인
    input_ports = mido.get_input_names()
    print("📋 사용 가능한 MIDI 입력 포트:")
    for i, port in enumerate(input_ports):
        print(f"  {i}: {port}")
    
    # Keystation 자동 선택
    keystation_port = None
    for port in input_ports:
        if "Keystation" in port and "USB MIDI" in port:
            keystation_port = port
            break
    
    if not keystation_port:
        print("❌ Keystation을 찾을 수 없습니다.")
        return
    
    print(f"\n🎹 연결: {keystation_port}")
    print("=" * 60)
    print("🎵 코드를 연주해보세요!")
    print("   - 2개 이상의 키를 동시에 누르면 코드를 분석합니다")
    print("   - 0.3초 이상 지속해야 정확한 분석이 됩니다")
    print("   - Ctrl+C로 종료")
    print("=" * 60)
    
    recognizer = RealtimeChordRecognizer()
    
    try:
        with mido.open_input(keystation_port) as inport:
            print("✅ MIDI 연결 성공! 지금 연주해보세요!\n")
            
            for message in inport:
                current_time = time.time()
                
                if message.type == 'note_on' and message.velocity > 0:
                    note_name = recognizer.note_names[message.note % 12]
                    octave = message.note // 12 - 1
                    print(f"🎵 키 눌림: {note_name}{octave} (세기: {message.velocity})")
                    
                    recognizer.add_note(message.note, message.velocity, current_time)
                
                elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                    note_name = recognizer.note_names[message.note % 12]
                    octave = message.note // 12 - 1
                    print(f"🎵 키 놓음: {note_name}{octave}")
                    
                    recognizer.remove_note(message.note, current_time)
    
    except KeyboardInterrupt:
        print("\n\n🛑 코드 인식 시스템 종료")
        print("👋 연주해주셔서 감사합니다!")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()