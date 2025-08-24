#!/usr/bin/env python3
"""
확장된 MIDI 테스트 - 더 자세한 정보와 긴 대기시간
"""

import rtmidi
import time

def detailed_midi_test():
    print("🎹 확장 MIDI 테스트")
    print("=" * 60)
    
    # 모든 MIDI 포트 정보 출력
    midi_in = rtmidi.MidiIn()
    ports = midi_in.get_ports()
    
    print("📋 감지된 모든 MIDI 포트:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port}")
    print()
    
    # 각 포트에서 메시지 확인
    for i, port_name in enumerate(ports):
        if "Keystation" in port_name:
            print(f"🔍 테스트 중: {port_name}")
            
            try:
                test_midi = rtmidi.MidiIn()
                test_midi.open_port(i)
                
                print(f"   ✅ 포트 {i} 연결 성공")
                print("   🎵 30초간 키보드를 쳐보세요...")
                
                start_time = time.time()
                message_count = 0
                
                while time.time() - start_time < 30:
                    msg = test_midi.get_message()
                    
                    if msg:
                        message_count += 1
                        message, deltatime = msg
                        
                        print(f"   📨 메시지 {message_count}: {message} (시간: {deltatime:.3f})")
                        
                        if len(message) >= 3:
                            status = message[0]
                            data1 = message[1]  
                            data2 = message[2]
                            
                            # 메시지 타입 분석
                            if status >= 144 and status <= 159:  # Note On
                                channel = status - 144
                                note = data1
                                velocity = data2
                                
                                if velocity > 0:
                                    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                                    octave = note // 12 - 1
                                    note_name = note_names[note % 12]
                                    
                                    print(f"      🎵 키 눌림: {note_name}{octave} (채널 {channel+1}, 세기 {velocity})")
                                else:
                                    print(f"      🎵 키 놓음: Note {note}")
                                    
                            elif status >= 128 and status <= 143:  # Note Off
                                channel = status - 128
                                note = data1
                                print(f"      🎵 키 놓음: Note {note} (채널 {channel+1})")
                                
                            elif status >= 176 and status <= 191:  # Control Change
                                channel = status - 176
                                controller = data1
                                value = data2
                                print(f"      🎛️ 컨트롤 변경: CC{controller}={value} (채널 {channel+1})")
                    
                    time.sleep(0.001)
                
                print(f"   📊 총 {message_count}개의 MIDI 메시지를 받았습니다.")
                test_midi.close_port()
                
            except Exception as e:
                print(f"   ❌ 포트 {i} 오류: {e}")
            
            print()

if __name__ == "__main__":
    detailed_midi_test()