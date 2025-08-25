#!/usr/bin/env python3
"""
C 코드 입력 시뮬레이션 - RAG 기반 즉흥 솔로 생성 시스템 출력 테스트
"""

import random
import time
from typing import List, Dict, Tuple

class ChordAnalyzer:
    """코드 분석 클래스"""
    
    def __init__(self):
        self.chord_database = {
            'C': {
                'notes': [60, 64, 67],  # C-E-G
                'type': 'major',
                'root': 60,
                'quality': 'bright',
                'mood': 'happy',
                'scale': [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
            }
        }
        
        # RAG 데이터베이스 - C 메이저 솔로 패턴들
        self.solo_patterns = {
            'C_major_basic': [60, 62, 64, 65, 67, 65, 64, 62],
            'C_major_jazzy': [60, 64, 67, 72, 69, 67, 65, 64],
            'C_major_blues': [60, 63, 65, 66, 67, 66, 65, 63],
            'C_major_classical': [60, 67, 64, 72, 67, 64, 60, 67],
            'C_major_pentatonic': [60, 62, 64, 67, 69, 72, 69, 67],
            'C_major_arpeggiated': [60, 64, 67, 72, 67, 64, 60, 64]
        }
        
        # 사용자 선호도 (학습된 데이터)
        self.user_preferences = {
            'jazz': 0.7,
            'blues': 0.8,
            'classical': 0.5,
            'rock': 0.6,
            'pentatonic': 0.9
        }
        
    def analyze_chord(self, chord_name: str) -> Dict:
        """코드 분석"""
        if chord_name in self.chord_database:
            return self.chord_database[chord_name]
        else:
            # 기본 C 코드 반환
            return self.chord_database['C']
    
    def generate_solo(self, chord_info: Dict) -> Tuple[List[int], str]:
        """RAG 기반 솔로 생성"""
        
        # 가중치 기반 패턴 선택
        pattern_weights = {
            'C_major_blues': self.user_preferences['blues'],
            'C_major_jazzy': self.user_preferences['jazz'],
            'C_major_pentatonic': self.user_preferences['pentatonic'],
            'C_major_classical': self.user_preferences['classical'],
            'C_major_basic': 0.3,
            'C_major_arpeggiated': 0.4
        }
        
        # 가중치에 따른 패턴 선택
        selected_pattern = max(pattern_weights.items(), key=lambda x: x[1])
        pattern_name = selected_pattern[0]
        confidence = selected_pattern[1]
        
        # 선택된 패턴 가져오기
        base_pattern = self.solo_patterns[pattern_name]
        
        # 패턴에 약간의 변형 추가 (RAG의 창의성 시뮬레이션)
        variations = []
        for note in base_pattern:
            # 10% 확률로 옥타브 변경
            if random.random() < 0.1:
                note += 12 if random.random() < 0.5 else -12
            # 5% 확률로 반음 변경
            elif random.random() < 0.05:
                note += 1 if random.random() < 0.5 else -1
            
            variations.append(max(36, min(84, note)))  # MIDI 범위 제한
        
        return variations, pattern_name
    
    def format_notes_for_output(self, notes: List[int]) -> List[str]:
        """MIDI 노트를 음표 이름으로 변환"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        formatted = []
        
        for note in notes:
            octave = note // 12 - 1
            note_name = note_names[note % 12]
            formatted.append(f"{note_name}{octave}")
        
        return formatted

def simulate_c_chord_input():
    """C 코드 입력 시뮬레이션 및 출력"""
    
    print("🎹 RAG 기반 즉흥 솔로 생성 시스템")
    print("=" * 60)
    print()
    
    # 시스템 초기화
    analyzer = ChordAnalyzer()
    
    print("📥 입력 감지: C 메이저 코드")
    print("   🎵 감지된 노트: C-E-G (MIDI: 60, 64, 67)")
    print()
    
    # 코드 분석 단계
    print("🔍 코드 분석 중...")
    time.sleep(0.5)
    
    chord_info = analyzer.analyze_chord('C')
    print(f"   ✅ 코드 타입: {chord_info['type'].upper()}")
    print(f"   🎨 음악적 특성: {chord_info['quality']}, {chord_info['mood']}")
    print(f"   🎼 추천 스케일: C Major")
    print()
    
    # RAG 검색 단계
    print("🧠 RAG 데이터베이스 검색 중...")
    time.sleep(0.5)
    
    print("   📚 관련 패턴 발견:")
    print("     - C Major Blues 패턴 (사용자 선호도: 80%)")
    print("     - C Major Pentatonic 패턴 (사용자 선호도: 90%)")  
    print("     - C Major Jazz 패턴 (사용자 선호도: 70%)")
    print("     - C Major Classical 패턴 (사용자 선호도: 50%)")
    print()
    
    # 솔로 생성 단계
    print("🎵 개인화된 솔로 생성 중...")
    time.sleep(0.5)
    
    solo_notes, pattern_used = analyzer.generate_solo(chord_info)
    formatted_notes = analyzer.format_notes_for_output(solo_notes)
    
    print(f"   🎯 선택된 패턴: {pattern_used.replace('_', ' ').title()}")
    print(f"   🎼 생성된 솔로 (MIDI): {solo_notes}")
    print(f"   🎵 생성된 솔로 (음표): {' → '.join(formatted_notes)}")
    print()
    
    # FL Studio 출력 시뮬레이션
    print("🎹 FL Studio 출력 시뮬레이션")
    print("   📤 채널 2로 MIDI 전송 중...")
    
    for i, (note, note_name) in enumerate(zip(solo_notes, formatted_notes)):
        time.sleep(0.3)  # 실제 연주 속도 시뮬레이션
        print(f"   🎵 Note {i+1}: {note_name} (MIDI {note}) - 재생 중...")
    
    print()
    print("✅ 솔로 생성 및 재생 완료!")
    print()
    
    # 학습 업데이트 시뮬레이션
    print("🧠 사용자 선호도 학습 업데이트...")
    print("   📈 Pentatonic 패턴 선호도: 90% → 92%")
    print("   💾 학습 데이터 저장 완료")
    print()
    
    print("🎯 시스템 상태:")
    print(f"   ⏱️ 응답 시간: 2.1초")
    print(f"   🎼 생성된 노트 수: {len(solo_notes)}개")
    print(f"   🎨 사용된 패턴: {pattern_used}")
    print(f"   📊 시스템 신뢰도: 95%")

if __name__ == "__main__":
    simulate_c_chord_input()