# '/Users/ohhalim/Documents/Image-Line/FL Studio/Settings/Hardware/Test Controller/device_test.py' 
# 위 디렉토리에 저장에서 mcp서버 연동

import transport
import midi
import channels
import time
import sys
import os

# RAG 시스템 import (프로젝트 루트 경로 추가)
project_root = "/Users/ohhalim/git_box/llm_fIstudio_mcp_rag_midi_Improvisation_program"
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from midi_rag_system import initialize_rag_system, generate_jazz_solo
    RAG_AVAILABLE = True
    print("RAG system loaded successfully")
except ImportError as e:
    print(f"RAG system not available: {e}")
    RAG_AVAILABLE = False

# 전역 변수
chord_input_mode = False
current_chord_progression = []
rag_system = None

# 화성코드 매핑 (MIDI 노트 -> 코드 심볼)
CHORD_MAP = {
    # 메이저 코드
    60: 'Cmaj7',    # C
    62: 'Dmaj7',    # D
    64: 'Emaj7',    # E
    65: 'Fmaj7',    # F
    67: 'Gmaj7',    # G
    69: 'Amaj7',    # A
    71: 'Bmaj7',    # B

    # 마이너 코드 (옥타브 위)
    72: 'Cm7',      # C
    74: 'Dm7',      # D
    76: 'Em7',      # E
    77: 'Fm7',      # F
    79: 'Gm7',      # G
    81: 'Am7',      # A
    83: 'Bm7',      # B

    # 도미넌트 7th (한 옥타브 더 위)
    84: 'C7',       # C
    86: 'D7',       # D
    88: 'E7',       # E
    89: 'F7',       # F
    91: 'G7',       # G
    93: 'A7',       # A
    95: 'B7'        # B
}

def OnInit():
    """Called when the script is loaded by FL Studio"""
    global rag_system
    print("Jazz Solo Generator with RAG System initialized")

    if RAG_AVAILABLE:
        try:
            rag_system = initialize_rag_system()
            print("RAG system ready for chord analysis")
        except Exception as e:
            print(f"Error initializing RAG system: {e}")

    print("Commands:")
    print("- Send chord progression as MIDI notes")
    print("- System will generate jazz solo automatically")
    print("- Chord mapping: C=60(maj7), C+12=72(m7), C+24=84(dom7)")

    return

def OnDeInit():
    """Called when the script is unloaded by FL Studio"""
    print("Jazz Solo Generator deinitialized")
    return

def OnMidiMsg(event, timestamp=0):
    """Called when a processed MIDI message is received"""

    # 전역 변수 초기화
    if 'receiving_mode' not in globals():
        global receiving_mode, note_count, midi_data, midi_notes_array
        global chord_input_mode, current_chord_progression
        receiving_mode = False
        note_count = 0
        midi_data = []
        midi_notes_array = []
        chord_input_mode = False
        current_chord_progression = []

    # Only process Note On messages with velocity > 0
    if event.status >= midi.MIDI_NOTEON and event.status < midi.MIDI_NOTEON + 16 and event.data2 > 0:
        note_value = event.data1

        # 특별한 제어 노트들
        if note_value == 0 and not receiving_mode:
            # 기존 솔로라인 수신 모드
            receiving_mode = True
            print("Started receiving solo line notes")
            midi_data = []
            note_count = 0
            midi_notes_array = []
            event.handled = True
            return

        elif note_value == 1 and not chord_input_mode:
            # 새로운 화성코드 입력 모드
            chord_input_mode = True
            current_chord_progression = []
            print("Started chord input mode - play chord progression")
            print("Press note 2 to generate solo line")
            event.handled = True
            return

        elif note_value == 2 and chord_input_mode:
            # 화성코드 입력 완료 및 솔로라인 생성
            chord_input_mode = False
            if current_chord_progression:
                print(f"Generating solo for chord progression: {current_chord_progression}")
                generate_and_record_solo(current_chord_progression)
            else:
                print("No chords entered")
            event.handled = True
            return

        # 화성코드 입력 모드일 때
        if chord_input_mode:
            chord_symbol = CHORD_MAP.get(note_value)
            if chord_symbol:
                current_chord_progression.append(chord_symbol)
                print(f"Added chord: {chord_symbol} (total: {len(current_chord_progression)})")
            else:
                print(f"Unknown chord for note {note_value}")
            event.handled = True
            return

        # 기존 솔로라인 수신 모드
        if receiving_mode:
            if note_count == 0:
                note_count = note_value
                print(f"Expecting {note_count} notes for solo line")
                event.handled = True
                return

            # All subsequent messages are MIDI values (6 per note)
            midi_data.append(note_value)

            # Process completed notes (every 6 values)
            if len(midi_data) >= 6 and len(midi_data) % 6 == 0:
                # Process the last complete note
                i = len(midi_data) - 6
                note = midi_data[i]
                velocity = midi_data[i+1]
                length_whole = midi_data[i+2]
                length_decimal = midi_data[i+3]
                position_whole = midi_data[i+4]
                position_decimal = midi_data[i+5]

                # Calculate full values
                length = length_whole + (length_decimal / 10.0)
                position = position_whole + (position_decimal / 10.0)

                # Add to notes array
                midi_notes_array.append((note, velocity, length, position))
                print(f"Added note: {note}, velocity={velocity}, length={length:.1f}, position={position:.1f}")

                if len(midi_notes_array) >= note_count or note_value == 127:
                    print(f"Recording solo line with {len(midi_notes_array)} notes")
                    receiving_mode = False

                    # Record the solo line
                    if midi_notes_array:
                        record_solo_line(midi_notes_array)

                    event.handled = True
                    return

            event.handled = True

def generate_and_record_solo(chord_progression):
    """화성코드 진행에 맞는 솔로라인 생성 및 녹음"""
    if not RAG_AVAILABLE or not rag_system:
        print("RAG system not available, generating basic solo")
        generate_basic_solo(chord_progression)
        return

    try:
        # RAG 시스템을 사용해 솔로라인 생성
        solo_line = rag_system.generate_solo_line(chord_progression, style='jazz')

        if solo_line:
            print(f"Generated {len(solo_line)} notes using RAG system")

            # FL Studio 형식으로 변환
            fl_notes = []
            for note_data in solo_line:
                fl_notes.append((
                    note_data['pitch'],
                    note_data['velocity'],
                    note_data['duration'],
                    note_data['offset']
                ))

            # 녹음
            record_solo_line(fl_notes)

        else:
            print("No solo generated, falling back to basic solo")
            generate_basic_solo(chord_progression)

    except Exception as e:
        print(f"Error in RAG solo generation: {e}")
        generate_basic_solo(chord_progression)

def generate_basic_solo(chord_progression):
    """기본 솔로라인 생성 (RAG 시스템 없을 때)"""
    print("Generating basic solo line")

    # 간단한 스케일 기반 솔로
    scale_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C 메이저 스케일
    basic_solo = []

    chord_duration = 2.0  # 각 코드당 2비트

    for i, chord in enumerate(chord_progression):
        # 코드에 맞는 노트들 선택
        for j in range(4):  # 각 코드당 4개 노트
            note_idx = (i * 4 + j) % len(scale_notes)
            pitch = scale_notes[note_idx] + 12  # 한 옥타브 위

            basic_solo.append((
                pitch,                                    # pitch
                100,                                      # velocity
                0.5,                                      # duration
                i * chord_duration + j * 0.5             # position
            ))

    print(f"Generated basic solo with {len(basic_solo)} notes")
    record_solo_line(basic_solo)

def record_solo_line(notes_array):
    """
    Records a batch of notes to FL Studio, handling simultaneous notes properly

    Args:
        notes_array: List of tuples, each containing (note, velocity, length_beats, position_beats)
    """
    print(f"Recording solo line with {len(notes_array)} notes...")

    # Sort notes by their starting position
    sorted_notes = sorted(notes_array, key=lambda x: x[3])

    # Group notes by their starting positions
    position_groups = {}
    for note in sorted_notes:
        position = note[3]  # position_beats is the 4th element (index 3)
        if position not in position_groups:
            position_groups[position] = []
        position_groups[position].append(note)

    # Process each position group
    positions = sorted(position_groups.keys())
    for position in positions:
        notes_at_position = position_groups[position]

        # Find the longest note in this group to determine recording length
        max_length = max(note[2] for note in notes_at_position)

        # Make sure transport is stopped first
        if transport.isPlaying():
            transport.stop()

        # Get the current channel
        channel = channels.selectedChannel()

        # Calculate ticks based on beats
        position_ticks = int(position * 1920)  # 1920 ticks per beat

        # Set playback position
        transport.setSongPos(position_ticks, 2)  # 2 = SONGLENGTH_ABSTICKS

        # Toggle recording mode if needed
        if not transport.isRecording():
            transport.record()

        print(f"Recording {len(notes_at_position)} simultaneous notes at position {position}")

        # Start playback to begin recording
        transport.start()

        # Record all notes at this position simultaneously
        for note, velocity, length, _ in notes_at_position:
            channels.midiNoteOn(channel, note, velocity)

        # Get the current tempo
        try:
            import mixer
            tempo = mixer.getCurrentTempo()
            tempo = tempo/1000
        except (ImportError, AttributeError):
            tempo = 120  # Default fallback

        print(f"Using tempo: {tempo} BPM")

        # Calculate the time to wait in seconds based on the longest note
        seconds_to_wait = (max_length * 60) / tempo

        print(f"Waiting for {seconds_to_wait:.2f} seconds...")

        # Wait the calculated time
        time.sleep(seconds_to_wait)

        # Send note-off events for all notes
        for note, _, _, _ in notes_at_position:
            channels.midiNoteOn(channel, note, 0)

        # Stop playback
        transport.stop()

        # Exit recording mode if it was active
        if transport.isRecording():
            transport.record()

        # Small pause between recordings to avoid potential issues
        time.sleep(0.2)

    print("Solo line recording complete!")

    # Return to beginning
    transport.setSongPos(0, 2)

def display_chord_mapping():
    """화성코드 매핑 정보 출력"""
    print("\nChord Mapping:")
    print("Major 7th chords (C4-B4):")
    for note in range(60, 72):
        if note in CHORD_MAP:
            print(f"  {note}: {CHORD_MAP[note]}")

    print("Minor 7th chords (C5-B5):")
    for note in range(72, 84):
        if note in CHORD_MAP:
            print(f"  {note}: {CHORD_MAP[note]}")

    print("Dominant 7th chords (C6-B6):")
    for note in range(84, 96):
        if note in CHORD_MAP:
            print(f"  {note}: {CHORD_MAP[note]}")

# 시작 시 매핑 정보 출력
if __name__ == "__main__":
    display_chord_mapping()