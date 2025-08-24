#!/usr/bin/env python3
"""
자동 MIDI 키보드 모니터 - 바로 모니터링 시작
"""

import mido
import time
from datetime import datetime

def get_note_name(note_number):
    """MIDI 노트 번호를 음표 이름으로 변환"""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = note_number // 12 - 1
    note_name = note_names[note_number % 12]
    return f"{note_name}{octave}"

def get_velocity_description(velocity):
    """벨로시티를 연주 강도 설명으로 변환"""
    if velocity == 0:
        return "놓음"
    elif velocity < 30:
        return "매우 약하게"
    elif velocity < 60:
        return "약하게"  
    elif velocity < 90:
        return "보통"
    elif velocity < 110:
        return "강하게"
    else:
        return "매우 강하게"

def main():
    print("🎹 FL Studio 호환 MIDI 키보드 자동 모니터")
    print("=" * 60)
    
    # MIDI 포트 목록 출력
    print("📋 사용 가능한 MIDI 입력 포트:")
    input_ports = mido.get_input_names()
    
    if not input_ports:
        print("  ❌ MIDI 입력 포트를 찾을 수 없습니다.")
        return
    
    for i, port in enumerate(input_ports):
        print(f"  {i}: {port}")
    
    # Keystation 자동 선택
    keystation_port = None
    for port in input_ports:
        if "Keystation" in port:
            keystation_port = port
            break
    
    if not keystation_port:
        print("\n❌ Keystation을 찾을 수 없습니다.")
        if input_ports:
            keystation_port = input_ports[0]
            print(f"첫 번째 포트 사용: {keystation_port}")
        else:
            return
    
    print(f"\n🎹 자동 선택: {keystation_port}")
    print("=" * 60)
    print("🎵 지금 키보드를 연주해보세요! (30초 후 자동 종료)")
    print("=" * 60)
    
    try:
        with mido.open_input(keystation_port) as inport:
            print("✅ MIDI 포트 연결 성공!")
            
            pressed_keys = set()
            note_count = 0
            start_time = time.time()
            
            # 30초 동안 모니터링
            while time.time() - start_time < 30:
                # 0.01초마다 메시지 확인
                message = inport.poll()
                
                if message:
                    current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    
                    if message.type == 'note_on':
                        note_name = get_note_name(message.note)
                        
                        if message.velocity > 0:
                            pressed_keys.add(message.note)
                            note_count += 1
                            velocity_desc = get_velocity_description(message.velocity)
                            print(f"🎵 [{current_time}] 🟢 {note_name} ({velocity_desc}, V:{message.velocity})")
                        else:
                            if message.note in pressed_keys:
                                pressed_keys.remove(message.note)
                            print(f"🎵 [{current_time}] 🔴 {note_name} (놓음)")
                    
                    elif message.type == 'note_off':
                        note_name = get_note_name(message.note)
                        if message.note in pressed_keys:
                            pressed_keys.remove(message.note)
                        print(f"🎵 [{current_time}] 🔴 {note_name} (놓음)")
                    
                    elif message.type == 'control_change':
                        control_name = get_control_name(message.control)
                        print(f"🎛️ [{current_time}] {control_name} = {message.value}")
                    
                    # 코드 표시
                    if len(pressed_keys) > 1:
                        pressed_notes = [get_note_name(note) for note in sorted(pressed_keys)]
                        print(f"   🎼 코드: {' + '.join(pressed_notes)}")
                
                time.sleep(0.01)  # 10ms 대기
            
            print(f"\n🛑 30초 모니터링 완료")
            print(f"📊 총 연주한 키: {note_count}개")
    
    except Exception as e:
        print(f"❌ 오류: {e}")
        print("💡 FL Studio가 MIDI 포트를 사용 중일 수 있습니다.")

def get_control_name(control_number):
    """컨트롤 번호를 이름으로 변환"""
    control_names = {
        1: "모드휠",
        7: "볼륨", 
        64: "서스테인 페달",
        120: "모든 사운드 오프",
        123: "모든 노트 오프"
    }
    return control_names.get(control_number, f"CC{control_number}")

if __name__ == "__main__":
    main()
    print("\n👋 모니터링이 종료되었습니다.")