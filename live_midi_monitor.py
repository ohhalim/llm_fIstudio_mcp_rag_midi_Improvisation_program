#!/usr/bin/env python3
"""
실시간 MIDI 키보드 모니터
연주하는 키를 실시간으로 감지하고 표시합니다.
"""

import rtmidi
import time
import threading
import sys

class LiveMidiMonitor:
    def __init__(self):
        self.midi_in = rtmidi.MidiIn()
        self.running = False
        self.pressed_keys = set()
        
    def get_note_name(self, note_number):
        """MIDI 노트 번호를 음표 이름으로 변환"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = note_number // 12 - 1
        note_name = note_names[note_number % 12]
        return f"{note_name}{octave}"
    
    def get_velocity_description(self, velocity):
        """벨로시티를 연주 강도로 변환"""
        if velocity < 30:
            return "매우 약하게"
        elif velocity < 60:
            return "약하게"
        elif velocity < 90:
            return "보통"
        elif velocity < 110:
            return "강하게"
        else:
            return "매우 강하게"
    
    def start_monitoring(self, port_index=1):  # Keystation 88 MK3 USB MIDI
        """실시간 MIDI 모니터링 시작"""
        
        available_ports = self.midi_in.get_ports()
        
        if not available_ports:
            print("❌ MIDI 입력 장비를 찾을 수 없습니다.")
            return
        
        if port_index >= len(available_ports):
            port_index = 0
        
        port_name = available_ports[port_index]
        
        try:
            self.midi_in.open_port(port_index)
            print(f"🎹 '{port_name}' 연결 성공!")
            print("=" * 60)
            print("🎵 연주를 시작하세요! (Ctrl+C로 종료)")
            print("=" * 60)
            
            self.running = True
            
            # 종료 감지용 스레드
            stop_thread = threading.Thread(target=self.wait_for_stop)
            stop_thread.daemon = True
            stop_thread.start()
            
            while self.running:
                msg = self.midi_in.get_message()
                
                if msg:
                    message, deltatime = msg
                    
                    if len(message) >= 3:
                        status = message[0]
                        note = message[1]
                        velocity = message[2]
                        
                        current_time = time.strftime("%H:%M:%S")
                        note_name = self.get_note_name(note)
                        
                        if status == 144 and velocity > 0:  # Note On
                            self.pressed_keys.add(note)
                            velocity_desc = self.get_velocity_description(velocity)
                            
                            print(f"🎵 [{current_time}] 🟢 {note_name} ({velocity_desc}, V:{velocity})")
                            
                        elif status == 128 or (status == 144 and velocity == 0):  # Note Off
                            if note in self.pressed_keys:
                                self.pressed_keys.remove(note)
                                print(f"🎵 [{current_time}] 🔴 {note_name} (놓음)")
                        
                        # 현재 눌린 키들 표시 (코드 표시)
                        if len(self.pressed_keys) > 1:
                            pressed_notes = [self.get_note_name(n) for n in sorted(self.pressed_keys)]
                            print(f"   🎼 현재 코드: {' + '.join(pressed_notes)}")
                
                time.sleep(0.001)  # CPU 사용률 최적화
                
        except KeyboardInterrupt:
            print("\n\n🛑 모니터링을 종료합니다.")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        finally:
            self.running = False
            self.midi_in.close_port()
            print("👋 MIDI 연결이 종료되었습니다.")
    
    def wait_for_stop(self):
        """키보드 입력 대기 (종료용)"""
        try:
            input("\n⏹️  [Enter]를 눌러서 종료하세요...\n")
        except:
            pass
        self.running = False

def main():
    print("🎹 실시간 MIDI 키보드 모니터")
    print("=" * 60)
    
    # 사용 가능한 MIDI 입력 장비 목록 표시
    midi_in = rtmidi.MidiIn()
    ports = midi_in.get_ports()
    
    print("📥 사용 가능한 MIDI 입력 장비:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port}")
    
    print()
    
    # Keystation 자동 선택
    keystation_port = -1
    for i, port in enumerate(ports):
        if "Keystation" in port and "USB MIDI" in port:
            keystation_port = i
            break
    
    if keystation_port != -1:
        print(f"✅ Keystation 88 MK3 자동 선택됨 (포트 {keystation_port})")
        
        monitor = LiveMidiMonitor()
        monitor.start_monitoring(keystation_port)
    else:
        print("❌ Keystation을 찾을 수 없습니다.")
        if ports:
            print(f"대신 첫 번째 장비를 사용합니다: {ports[0]}")
            monitor = LiveMidiMonitor()
            monitor.start_monitoring(0)

if __name__ == "__main__":
    main()