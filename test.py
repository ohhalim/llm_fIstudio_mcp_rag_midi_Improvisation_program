#!/usr/bin/env python3
"""
test.py - 화성코드 입력 및 솔로라인 출력 테스트

기능:
1. 화성코드를 FL Studio에 입력
2. MCP가 읽어서 관련 솔로라인 생성 및 출력
"""

import mido
import time
from mido import Message

# MIDI 포트 설정
MIDI_PORT_NAME = 'IAC ÎìúÎùºÏù¥Î≤Ñ Î≤ÑÏä§ 1'

# 화성코드 매핑 (MIDI note → Chord symbol)
CHORD_MAP = {
    # 메이저 7th 코드 (60-71)
    60: 'Cmaj7',    # C
    62: 'Dmaj7',    # D
    64: 'Emaj7',    # E
    65: 'Fmaj7',    # F
    67: 'Gmaj7',    # G
    69: 'Amaj7',    # A
    71: 'Bmaj7',    # B

    # 마이너 7th 코드 (72-83)
    72: 'Cm7',      # C
    74: 'Dm7',      # D
    76: 'Em7',      # E
    77: 'Fm7',      # F
    79: 'Gm7',      # G
    81: 'Am7',      # A
    83: 'Bm7',      # B

    # 도미넌트 7th 코드 (84-95)
    84: 'C7',       # C
    86: 'D7',       # D
    88: 'E7',       # E
    89: 'F7',       # F
    91: 'G7',       # G
    93: 'A7',       # A
    95: 'B7'        # B
}

# 화성코드별 솔로 노트 패턴
CHORD_SOLO_PATTERNS = {
    'Cmaj7': [72, 76, 79, 84],      # C, E, G, C (1, 3, 5, 8)
    'Dm7': [74, 77, 81, 86],        # D, F, A, D
    'Em7': [76, 79, 83, 88],        # E, G, B, E
    'Fmaj7': [77, 81, 84, 89],      # F, A, C, F
    'Gm7': [79, 82, 86, 91],        # G, Bb, D, G
    'G7': [79, 83, 86, 89],         # G, B, D, F
    'Am7': [81, 84, 88, 93],        # A, C, E, A
    'A7': [81, 85, 88, 91],         # A, C#, E, G
    'Bm7': [83, 86, 90, 95],        # B, D, F#, B
}

class ChordSoloTester:
    def __init__(self):
        self.output_port = None
        self.connect_midi()

    def connect_midi(self):
        """MIDI 포트 연결"""
        try:
            self.output_port = mido.open_output(MIDI_PORT_NAME)
            print(f"✅ MIDI 포트 연결 성공: {MIDI_PORT_NAME}")
        except Exception as e:
            print(f"❌ MIDI 포트 연결 실패: {e}")
            print("사용 가능한 포트:")
            for port in mido.get_output_names():
                print(f"  - {port}")

    def send_midi_note(self, note, velocity=100, duration=0.1):
        """MIDI 노트 전송"""
        if not self.output_port:
            print("MIDI 포트가 연결되지 않음")
            return

        try:
            # Note On
            note_on = Message('note_on', note=note, velocity=velocity)
            self.output_port.send(note_on)

            # Duration 대기
            time.sleep(duration)

            # Note Off
            note_off = Message('note_off', note=note, velocity=0)
            self.output_port.send(note_off)

            print(f"🎵 MIDI Note {note} 전송됨")

        except Exception as e:
            print(f"❌ MIDI 전송 오류: {e}")

    def send_chord_progression_mode(self):
        """화성코드 입력 모드 시작 신호 전송"""
        print("🎯 화성코드 입력 모드 시작...")
        self.send_midi_note(1)  # FL Studio device_test.py의 화성코드 모드
        time.sleep(0.1)

    def send_chord(self, chord_note):
        """화성코드 전송"""
        chord_name = CHORD_MAP.get(chord_note, f"Unknown({chord_note})")
        print(f"🎼 화성코드 전송: {chord_name} (MIDI {chord_note})")
        self.send_midi_note(chord_note)
        time.sleep(0.2)

    def send_generate_solo_signal(self):
        """솔로라인 생성 신호 전송"""
        print("🎸 솔로라인 생성 신호 전송...")
        self.send_midi_note(2)  # FL Studio device_test.py의 솔로 생성 신호
        time.sleep(0.1)

    def generate_local_solo(self, chord_progression):
        """로컬에서 솔로라인 생성 (테스트용)"""
        print(f"🎶 로컬 솔로 생성: {chord_progression}")

        solo_notes = []

        for i, chord in enumerate(chord_progression):
            # 기본 패턴이 있으면 사용, 없으면 스케일 기반
            if chord in CHORD_SOLO_PATTERNS:
                pattern = CHORD_SOLO_PATTERNS[chord]
                print(f"  {chord}: {pattern}")
            else:
                # 기본 C 메이저 스케일
                pattern = [72, 74, 76, 77]  # C, D, E, F
                print(f"  {chord}: 기본 패턴 {pattern}")

            # 각 코드당 4개 노트 추가
            for j, note in enumerate(pattern):
                solo_notes.append({
                    'pitch': note,
                    'velocity': 80 + (j * 5),  # 점진적으로 벨로시티 증가
                    'duration': 0.5,
                    'position': i * 2.0 + j * 0.5  # 각 코드당 2비트
                })

        return solo_notes

    def send_solo_line(self, solo_notes):
        """생성된 솔로라인을 FL Studio로 전송"""
        print(f"📤 솔로라인 전송: {len(solo_notes)} 노트")

        # trigger.py 형식으로 전송
        # 시작 신호
        self.send_midi_note(0, duration=0.01)
        time.sleep(0.01)

        # 노트 개수
        self.send_midi_note(len(solo_notes), duration=0.01)
        time.sleep(0.01)

        # 각 노트 전송
        for note_data in solo_notes:
            pitch = note_data['pitch']
            velocity = note_data['velocity']
            length = note_data['duration']
            position = note_data['position']

            # MIDI 데이터 전송 (trigger.py 형식)
            self.send_midi_note(min(127, max(0, int(pitch))), duration=0.01)
            self.send_midi_note(min(127, max(0, int(velocity))), duration=0.01)

            length_whole = min(127, int(length))
            self.send_midi_note(length_whole, duration=0.01)

            length_decimal = int(round((length - length_whole) * 10)) % 10
            self.send_midi_note(length_decimal, duration=0.01)

            position_whole = min(127, int(position))
            self.send_midi_note(position_whole, duration=0.01)

            position_decimal = int(round((position - position_whole) * 10)) % 10
            self.send_midi_note(position_decimal, duration=0.01)

            print(f"  📝 {pitch}, vel:{velocity}, len:{length}, pos:{position}")

        # 종료 신호
        self.send_midi_note(127, duration=0.01)
        print("✅ 솔로라인 전송 완료!")

    def test_basic_chord_progression(self):
        """기본 화성진행 테스트: ii-V-I"""
        print("\n🧪 기본 화성진행 테스트: Dm7 - G7 - Cmaj7")

        # 1. 화성코드 입력 모드 시작
        self.send_chord_progression_mode()

        # 2. 화성진행 입력
        chord_progression = ['Dm7', 'G7', 'Cmaj7']
        chord_notes = [74, 91, 60]  # Dm7, G7, Cmaj7

        for chord_note in chord_notes:
            self.send_chord(chord_note)

        # 3. 솔로라인 생성 신호
        self.send_generate_solo_signal()

        print("📊 FL Studio에서 솔로라인이 생성되어야 합니다.")

    def test_direct_solo_generation(self):
        """직접 솔로라인 생성 및 전송 테스트"""
        print("\n🧪 직접 솔로라인 생성 테스트")

        # 화성진행
        chord_progression = ['Cmaj7', 'Am7', 'Dm7', 'G7']

        # 솔로라인 생성
        solo_notes = self.generate_local_solo(chord_progression)

        # FL Studio로 전송
        self.send_solo_line(solo_notes)

    def close(self):
        """연결 종료""" 
        if self.output_port:
            self.output_port.close()
            print("🔌 MIDI 포트 연결 종료")

def main():
    """메인 실행 함수"""
    print("🎹 화성코드 → 솔로라인 테스트 시작")
    print("=" * 50)

    tester = ChordSoloTester()

    try:
        # 테스트 선택
        print("\n테스트 선택:")
        print("1. 기본 화성진행 테스트 (FL Studio device_test.py 사용)")
        print("2. 직접 솔로라인 생성 테스트 (trigger.py 사용)")
        print("3. 둘 다 테스트")

        # 자동으로 테스트 3 실행 (둘 다 테스트)
        choice = '3'
        print("자동 선택: 3 (둘 다 테스트)")

        if choice == '1':
            tester.test_basic_chord_progression()
        elif choice == '2':
            tester.test_direct_solo_generation()
        elif choice == '3':
            tester.test_basic_chord_progression()
            time.sleep(2)
            tester.test_direct_solo_generation()
        else:
            print("❌ 잘못된 선택")

    except KeyboardInterrupt:
        print("\n⏹️  테스트 중단됨")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        tester.close()

if __name__ == "__main__":
    main()