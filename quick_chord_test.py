#!/usr/bin/env python3
"""
빠른 코드 인식 테스트 - 10초간만 실행
"""

import mido
import time
from datetime import datetime

def quick_test():
    print("🎹 빠른 코드 인식 테스트 (10초)")
    print("=" * 50)
    
    input_ports = mido.get_input_names()
    
    keystation_port = None
    for port in input_ports:
        if "Keystation" in port and "USB MIDI" in port:
            keystation_port = port
            break
    
    if not keystation_port:
        print("❌ Keystation 포트를 찾을 수 없습니다.")
        print("사용 가능한 포트:", input_ports)
        return
    
    print(f"🎹 연결 중: {keystation_port}")
    
    current_notes = set()
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    try:
        with mido.open_input(keystation_port) as inport:
            print("✅ 연결 성공! 지금 코드를 연주하세요!")
            
            start_time = time.time()
            note_count = 0
            
            while time.time() - start_time < 10:  # 10초간만 실행
                message = inport.poll()
                
                if message:
                    note_count += 1
                    current_time = datetime.now().strftime("%H:%M:%S")
                    
                    if message.type == 'note_on' and message.velocity > 0:
                        note_class = message.note % 12
                        current_notes.add(note_class)
                        
                        note_name = note_names[note_class]
                        octave = message.note // 12 - 1
                        print(f"🎵 [{current_time}] +{note_name}{octave} (V:{message.velocity})")
                        
                        # 즉시 코드 분석
                        if len(current_notes) >= 3:
                            analyze_chord(current_notes, note_names)
                    
                    elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
                        note_class = message.note % 12
                        current_notes.discard(note_class)
                        
                        note_name = note_names[note_class]
                        octave = message.note // 12 - 1
                        print(f"🎵 [{current_time}] -{note_name}{octave}")
                
                time.sleep(0.01)
            
            print(f"\n📊 10초 동안 {note_count}개 MIDI 메시지 수신")
            
    except Exception as e:
        print(f"❌ 오류: {e}")

def analyze_chord(notes, note_names):
    """간단한 코드 분석"""
    if len(notes) < 3:
        return
    
    # 정렬된 노트 리스트
    sorted_notes = sorted(list(notes))
    
    # 각 노트를 루트로 시도
    for root in sorted_notes:
        intervals = [(note - root) % 12 for note in sorted_notes]
        intervals.sort()
        
        # 기본 코드 패턴 매칭
        chord_type = identify_chord(intervals)
        if chord_type:
            chord_name = f"{note_names[root]} {chord_type}"
            note_list = [note_names[note] for note in sorted_notes]
            
            print(f"🎼 코드 인식: {chord_name}")
            print(f"   구성음: {' + '.join(note_list)}")
            return

def identify_chord(intervals):
    """간격 패턴으로 코드 식별"""
    interval_patterns = {
        (0, 4, 7): "major",
        (0, 3, 7): "minor",
        (0, 4, 7, 11): "maj7",
        (0, 4, 7, 10): "dom7",
        (0, 3, 7, 10): "min7",
        (0, 3, 6): "dim",
        (0, 4, 8): "aug",
        (0, 5, 7): "sus4",
        (0, 2, 7): "sus2"
    }
    
    return interval_patterns.get(tuple(intervals), None)

if __name__ == "__main__":
    quick_test()
    print("👋 테스트 완료")