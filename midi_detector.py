#!/usr/bin/env python3
"""
MIDI 장비 감지 스크립트
연결된 MIDI 입력/출력 장비를 확인합니다.
"""

import rtmidi

def detect_midi_devices():
    """연결된 MIDI 장비들을 감지하고 출력합니다."""
    
    print("🎹 MIDI 장비 감지 중...")
    print("=" * 50)
    
    # MIDI 입력 장비 감지
    midi_in = rtmidi.MidiIn()
    available_inputs = midi_in.get_ports()
    
    print(f"📥 MIDI 입력 장비 ({len(available_inputs)}개):")
    if available_inputs:
        for i, port_name in enumerate(available_inputs):
            print(f"  {i}: {port_name}")
    else:
        print("  연결된 MIDI 입력 장비가 없습니다.")
    
    print()
    
    # MIDI 출력 장비 감지  
    midi_out = rtmidi.MidiOut()
    available_outputs = midi_out.get_ports()
    
    print(f"📤 MIDI 출력 장비 ({len(available_outputs)}개):")
    if available_outputs:
        for i, port_name in enumerate(available_outputs):
            print(f"  {i}: {port_name}")
    else:
        print("  연결된 MIDI 출력 장비가 없습니다.")
    
    print("=" * 50)
    
    # 마스터 키보드 감지 (일반적인 키워드로 필터링)
    keyboard_keywords = ['keyboard', 'keys', 'midi', 'piano', 'synth', 'controller']
    
    found_keyboards = []
    for port in available_inputs:
        for keyword in keyboard_keywords:
            if keyword.lower() in port.lower():
                found_keyboards.append(port)
                break
    
    if found_keyboards:
        print("🎹 감지된 마스터 키보드:")
        for kb in found_keyboards:
            print(f"  ✅ {kb}")
    else:
        print("🎹 마스터 키보드를 찾지 못했습니다.")
        if available_inputs:
            print("   (하지만 MIDI 입력 장비는 있습니다)")
    
    return available_inputs, available_outputs

def test_midi_input(port_index=0):
    """선택한 MIDI 입력 장비에서 메시지를 받아봅니다."""
    
    midi_in = rtmidi.MidiIn()
    available_inputs = midi_in.get_ports()
    
    if not available_inputs:
        print("❌ MIDI 입력 장비가 없습니다.")
        return
    
    if port_index >= len(available_inputs):
        print(f"❌ 포트 인덱스 {port_index}가 범위를 벗어났습니다.")
        return
    
    port_name = available_inputs[port_index]
    print(f"🎹 '{port_name}' 연결 중...")
    
    try:
        midi_in.open_port(port_index)
        print(f"✅ 연결 성공! 키를 눌러보세요... (10초간 대기)")
        
        import time
        start_time = time.time()
        
        while time.time() - start_time < 10:
            msg = midi_in.get_message()
            
            if msg:
                message, deltatime = msg
                
                # MIDI 메시지 해석
                if len(message) >= 3:
                    status = message[0]
                    note = message[1]
                    velocity = message[2]
                    
                    if status == 144:  # Note On
                        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                        octave = note // 12 - 1
                        note_name = note_names[note % 12]
                        print(f"🎵 키 눌림: {note_name}{octave} (Note {note}, Velocity {velocity})")
                    
                    elif status == 128:  # Note Off
                        print(f"🎵 키 놓음: Note {note}")
            
            time.sleep(0.01)
        
        print("⏰ 10초 경과. 테스트 종료.")
        midi_in.close_port()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    inputs, outputs = detect_midi_devices()
    
    # MIDI 입력이 있으면 테스트 제안
    if inputs:
        print()
        response = input("MIDI 키보드 테스트를 해보시겠습니까? (y/n): ")
        if response.lower() == 'y':
            test_midi_input(0)  # 첫 번째 입력 장비로 테스트