#!/usr/bin/env python3
"""
mido를 사용한 MIDI 키보드 입력 모니터
FL Studio와 호환되는 방식으로 MIDI 입력을 감지합니다.
"""

import mido
import time
from datetime import datetime

def list_midi_ports():
    """사용 가능한 MIDI 포트 목록 출력"""
    print("🎹 MIDI 입력 포트 목록:")
    input_ports = mido.get_input_names()
    
    if not input_ports:
        print("  ❌ MIDI 입력 포트를 찾을 수 없습니다.")
        return []
    
    for i, port in enumerate(input_ports):
        print(f"  {i}: {port}")
    
    print("\n🔊 MIDI 출력 포트 목록:")
    output_ports = mido.get_output_names()
    
    for i, port in enumerate(output_ports):
        print(f"  {i}: {port}")
    
    return input_ports

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

def monitor_keystation():
    """Keystation 88 MK3 모니터링"""
    
    # 사용 가능한 포트 목록 출력
    input_ports = list_midi_ports()
    
    if not input_ports:
        print("❌ MIDI 입력 포트가 없습니다.")
        return
    
    # Keystation 포트 찾기
    keystation_port_name = None
    for port in input_ports:
        if "Keystation" in port:
            keystation_port_name = port
            break
    
    if not keystation_port_name:
        print("❌ Keystation을 찾을 수 없습니다.")
        print("첫 번째 포트로 시도합니다...")
        keystation_port_name = input_ports[0]
    
    print(f"\n🎹 연결 시도: {keystation_port_name}")
    
    try:
        # MIDI 입력 포트 열기
        with mido.open_input(keystation_port_name) as inport:
            print("✅ MIDI 포트 연결 성공!")
            print("=" * 60)
            print("🎵 키보드를 연주해보세요! (Ctrl+C로 종료)")
            print("=" * 60)
            
            pressed_keys = set()  # 현재 눌린 키들 추적
            note_count = 0
            
            # 무한 루프로 MIDI 메시지 수신
            for message in inport:
                current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                
                # Note On 메시지
                if message.type == 'note_on':
                    note_name = get_note_name(message.note)
                    velocity_desc = get_velocity_description(message.velocity)
                    
                    if message.velocity > 0:
                        pressed_keys.add(message.note)
                        note_count += 1
                        print(f"🎵 [{current_time}] 🟢 {note_name} ({velocity_desc}, V:{message.velocity}, CH:{message.channel + 1})")
                    else:
                        # velocity가 0인 note_on은 실제로는 note_off
                        if message.note in pressed_keys:
                            pressed_keys.remove(message.note)
                        print(f"🎵 [{current_time}] 🔴 {note_name} (놓음, CH:{message.channel + 1})")
                
                # Note Off 메시지
                elif message.type == 'note_off':
                    note_name = get_note_name(message.note)
                    if message.note in pressed_keys:
                        pressed_keys.remove(message.note)
                    print(f"🎵 [{current_time}] 🔴 {note_name} (놓음, CH:{message.channel + 1})")
                
                # Control Change 메시지 (페달, 모드휠 등)
                elif message.type == 'control_change':
                    control_name = get_control_name(message.control)
                    print(f"🎛️ [{current_time}] {control_name} (CC{message.control}) = {message.value}")
                
                # Pitch Bend 메시지
                elif message.type == 'pitchwheel':
                    print(f"🎵 [{current_time}] 피치벤드: {message.pitch}")
                
                # Program Change 메시지
                elif message.type == 'program_change':
                    print(f"🎛️ [{current_time}] 프로그램 변경: {message.program}")
                
                # 현재 눌린 키들 표시 (코드)
                if len(pressed_keys) > 1:
                    pressed_notes = [get_note_name(note) for note in sorted(pressed_keys)]
                    print(f"   🎼 현재 코드: {' + '.join(pressed_notes)} ({len(pressed_keys)}개 키)")
                
                # 통계 업데이트
                if note_count % 10 == 0 and note_count > 0:
                    print(f"📊 총 연주한 키: {note_count}개")
    
    except KeyboardInterrupt:
        print(f"\n\n🛑 모니터링 종료")
        print(f"📊 총 연주한 키: {note_count}개")
        print("👋 FL Studio와 함께 즐거운 음악 작업 되세요!")
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("💡 해결 방법:")
        print("  1. FL Studio가 MIDI 포트를 점유하고 있지 않은지 확인")
        print("  2. Keystation이 제대로 연결되어 있는지 확인")
        print("  3. macOS 시스템 설정에서 MIDI 권한 확인")

def get_control_name(control_number):
    """컨트롤 체인지 번호를 이름으로 변환"""
    control_names = {
        1: "모드휠",
        7: "볼륨",
        10: "팬",
        11: "익스프레션",
        64: "서스테인 페달",
        65: "포르타멘토",
        66: "소스테누토",
        67: "소프트 페달",
        120: "모든 사운드 오프",
        121: "컨트롤러 리셋",
        123: "모든 노트 오프"
    }
    
    return control_names.get(control_number, f"컨트롤 {control_number}")

def test_midi_output():
    """MIDI 출력 테스트 (FL Studio로 노트 전송)"""
    output_ports = mido.get_output_names()
    
    print("🔊 MIDI 출력 테스트")
    print("사용 가능한 출력 포트:")
    for i, port in enumerate(output_ports):
        print(f"  {i}: {port}")
    
    # FL Studio용 포트 찾기
    fl_port = None
    for port in output_ports:
        if "loopMIDI" in port or "FL Studio" in port:
            fl_port = port
            break
    
    if fl_port:
        print(f"\n🎹 FL Studio로 테스트 노트 전송: {fl_port}")
        try:
            with mido.open_output(fl_port) as outport:
                # C major 코드 전송
                test_notes = [60, 64, 67]  # C, E, G
                
                print("🎵 C major 코드 전송...")
                for note in test_notes:
                    outport.send(mido.Message('note_on', note=note, velocity=80))
                    print(f"  노트 온: {get_note_name(note)}")
                
                time.sleep(1)  # 1초 유지
                
                for note in test_notes:
                    outport.send(mido.Message('note_off', note=note))
                    print(f"  노트 오프: {get_note_name(note)}")
                
                print("✅ 테스트 완료!")
        
        except Exception as e:
            print(f"❌ 출력 테스트 실패: {e}")

if __name__ == "__main__":
    print("🎹 FL Studio 호환 MIDI 키보드 모니터")
    print("=" * 60)
    
    # 선택 메뉴
    print("원하는 작업을 선택하세요:")
    print("1. MIDI 입력 모니터링 (키보드 연주 감지)")
    print("2. MIDI 출력 테스트 (FL Studio로 노트 전송)")
    print("3. 포트 목록만 보기")
    
    try:
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == "1":
            monitor_keystation()
        elif choice == "2":
            test_midi_output()
        elif choice == "3":
            list_midi_ports()
        else:
            print("기본값으로 MIDI 입력 모니터링을 시작합니다...")
            monitor_keystation()
    
    except KeyboardInterrupt:
        print("\n👋 프로그램을 종료합니다.")