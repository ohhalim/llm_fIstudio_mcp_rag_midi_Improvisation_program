#!/usr/bin/env python3
"""
간단한 MIDI 테스트 - 10초간 연주 감지
"""

import rtmidi
import time

def listen_for_10_seconds():
    print("🎹 MIDI 키보드 연주 감지 시작!")
    print("=" * 50)
    
    midi_in = rtmidi.MidiIn()
    ports = midi_in.get_ports()
    
    # Keystation 찾기
    keystation_port = -1
    for i, port in enumerate(ports):
        if "Keystation" in port and "USB MIDI" in port:
            keystation_port = i
            break
    
    if keystation_port == -1:
        print("❌ Keystation을 찾을 수 없습니다.")
        return
    
    try:
        midi_in.open_port(keystation_port)
        print(f"✅ 연결됨: {ports[keystation_port]}")
        print("🎵 지금 키보드를 쳐보세요! (10초간 감지)")
        print("=" * 50)
        
        start_time = time.time()
        note_count = 0
        
        while time.time() - start_time < 10:
            msg = midi_in.get_message()
            
            if msg:
                message, deltatime = msg
                
                if len(message) >= 3:
                    status = message[0]
                    note = message[1]
                    velocity = message[2]
                    
                    if status == 144 and velocity > 0:  # Note On
                        note_count += 1
                        
                        # 음표 이름 계산
                        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                        octave = note // 12 - 1
                        note_name = note_names[note % 12]
                        
                        # 연주 강도
                        if velocity < 30:
                            strength = "약하게"
                        elif velocity < 60:
                            strength = "보통"
                        elif velocity < 90:
                            strength = "강하게"
                        else:
                            strength = "매우 강하게"
                        
                        elapsed = time.time() - start_time
                        print(f"🎵 [{elapsed:.1f}s] {note_name}{octave} ({strength}, V:{velocity})")
            
            time.sleep(0.01)
        
        print("=" * 50)
        print(f"🎉 10초 동안 총 {note_count}개의 키를 눌렀습니다!")
        midi_in.close_port()
        
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    listen_for_10_seconds()