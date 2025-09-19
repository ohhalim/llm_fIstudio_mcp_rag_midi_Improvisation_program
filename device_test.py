# device_test.py
# name=Test Controller

import transport
import midi
import channels
import time

# 전역 변수
receiving_mode = False
note_count = 0
midi_data = []
midi_notes_array = []

def OnInit():
    """Called when the script is loaded by FL Studio"""
    print("Basic MIDI Solo Generator initialized")
    print("Commands:")
    print("- Send MIDI note 1: Start recording mode")
    print("- Send MIDI note 2: Stop recording and generate solo")
    return

def OnDeInit():
    """Called when the script is unloaded by FL Studio"""
    print("Basic MIDI Solo Generator deinitialized")
    return

def OnMidiMsg(event, timestamp=0):
    """Called when a processed MIDI message is received"""

    # 전역 변수 초기화
    if 'receiving_mode' not in globals():
        global receiving_mode, note_count, midi_data, midi_notes_array
        receiving_mode = False
        note_count = 0
        midi_data = []
        midi_notes_array = []

    # Only process Note On messages with velocity > 0
    if event.status >= midi.MIDI_NOTEON and event.status < midi.MIDI_NOTEON + 16 and event.data2 > 0:
        note_value = event.data1

        # 명령어 처리
        if note_value == 1:  # MIDI note 1: 녹음 모드 시작
            print("Starting MIDI recording mode...")
            receiving_mode = True
            note_count = 0
            midi_data.clear()
            midi_notes_array.clear()

        elif note_value == 2:  # MIDI note 2: 녹음 중지 및 솔로 생성
            print("Stopping recording and generating solo...")
            receiving_mode = False
            generate_and_record_solo()

        elif receiving_mode:
            # 녹음 모드일 때 MIDI 데이터 수집
            note_count += 1
            midi_data.append({
                'note': note_value,
                'velocity': event.data2,
                'timestamp': time.time()
            })
            midi_notes_array.append(note_value)
            print(f"Recorded note {note_count}: {note_value}")

            # 4개 노트 수집하면 자동으로 솔로 생성
            if note_count >= 4:
                print("Auto-generating solo after 4 notes...")
                receiving_mode = False
                generate_and_record_solo()

        event.handled = True

def generate_and_record_solo():
    """기본 솔로라인 생성 및 녹음"""
    if not midi_notes_array:
        print("No MIDI data to process")
        return

    print(f"Generating solo from {len(midi_notes_array)} notes")

    # 간단한 솔로라인 생성 (기본 스케일)
    scale_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C 메이저 스케일
    solo_notes = []

    # 8개 노트로 솔로라인 생성
    for i in range(8):
        note_idx = i % len(scale_notes)
        pitch = scale_notes[note_idx] + 12  # 한 옥타브 위
        velocity = 80
        duration = 0.5  # 반 비트
        offset = i * 0.5  # 시간 간격

        solo_notes.append((pitch, velocity, duration, offset))

    print(f"Generated {len(solo_notes)} solo notes")
    record_solo_line(solo_notes)

def record_solo_line(notes):
    """FL Studio에서 솔로라인 녹음"""
    if not notes:
        print("No notes to record")
        return

    print(f"Recording {len(notes)} notes to FL Studio...")

    # 녹음 시작
    transport.setRecording(True, midi.REC_MIDI)

    start_time = time.time()

    # 각 노트를 순차적으로 전송
    for pitch, velocity, duration, offset in notes:
        # 시간 대기
        target_time = start_time + offset
        while time.time() < target_time:
            time.sleep(0.001)

        # Note On
        midi.midiOutNewMsg(
            midi.MIDI_NOTEON,
            0,  # channel
            int(pitch),
            int(velocity)
        )

        # Note Off (duration 후)
        time.sleep(duration)
        midi.midiOutNewMsg(
            midi.MIDI_NOTEOFF,
            0,  # channel
            int(pitch),
            0
        )

    # 녹음 중지
    time.sleep(0.1)
    transport.setRecording(False)

    print("Solo recording completed!")