from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import mido
from mido import Message
import time
import threading

# --- Configuration ---
# MCP 서버 설정
mcp = FastMCP("flstudio_solo_generator")

# MIDI 포트 설정
# controller.py -> FL Studio (솔로 멜로디 전송용)
OUTPUT_PORT_NAME = 'IAC ÎìúÎùºÏù¥Î≤Ñ loopMIDI Port 2'
# FL Studio -> controller.py (코드 입력용)
INPUT_PORT_NAME = 'IAC ÎìúÎùºÏù¥Î≤Ñ loopMIDI Port 3'

# --- MIDI I/O Initialization ---
try:
    output_port = mido.open_output(OUTPUT_PORT_NAME)
    input_port = mido.open_input(INPUT_PORT_NAME)
    print(f"Successfully opened MIDI ports:")
    print(f"  - Output: {OUTPUT_PORT_NAME}")
    print(f"  - Input: {INPUT_PORT_NAME}")
except (OSError, IOError) as e:
    print(f"Error opening MIDI ports: {e}")
    print("Please ensure 'loopMIDI' is running and the ports are named correctly.")
    # 포트가 없으면 실행을 중단하거나, 가상 포트를 사용하도록 설정할 수 있습니다.
    # 여기서는 일단 에러 메시지를 출력하고 진행합니다.
    output_port = None
    input_port = None

# --- Music Theory & Solo Generation ---

def get_chord_details(chord_notes):
    """
    코드 노트를 분석하여 루트 노트와 코드 타입(Major/Minor)을 반환합니다.
    """
    if not chord_notes:
        return None, None

    # 노트를 정렬하여 루트를 찾기 쉽게 만듭니다.
    sorted_notes = sorted(list(set(chord_notes)))
    root_note = sorted_notes[0]
    
    # 3화음의 간격(interval)을 분석합니다.
    intervals = [note - root_note for note in sorted_notes]

    # Major chord: Root, Major Third (4), Perfect Fifth (7)
    if 4 in intervals and 7 in intervals:
        return root_note, 'Major'
    # Minor chord: Root, Minor Third (3), Perfect Fifth (7)
    if 3 in intervals and 7 in intervals:
        return root_note, 'Minor'
    
    return root_note, 'Unknown' # 다른 종류의 코드는 일단 'Unknown'으로 처리

def generate_solo_notes(root_note, chord_type, start_pos, num_bars=1):
    """
    주어진 코드에 맞춰 솔로 라인을 생성합니다.
    """
    solo_notes = []
    
    # 코드 타입에 맞는 스케일을 정의합니다.
    if chord_type == 'Major':
        # C Major Scale intervals: 0, 2, 4, 5, 7, 9, 11
        scale = [0, 2, 4, 5, 7, 9, 11] 
    elif chord_type == 'Minor':
        # C Natural Minor Scale intervals: 0, 2, 3, 5, 7, 8, 10
        scale = [0, 2, 3, 5, 7, 8, 10]
    else:
        # 모르는 코드는 일단 메이저 스케일로 처리
        scale = [0, 2, 4, 5, 7, 9, 11]

    # 솔로 멜로디 생성 (간단한 아르페지오 + 스케일)
    
    # 1. Arpeggio
    solo_notes.append({'note': root_note + 12, 'velocity': 100, 'length': 0.4, 'position': start_pos + 0.0})
    solo_notes.append({'note': root_note + 12 + scale[2], 'velocity': 90, 'length': 0.4, 'position': start_pos + 0.5})
    solo_notes.append({'note': root_note + 12 + scale[4], 'velocity': 95, 'length': 0.4, 'position': start_pos + 1.0})

    # 2. Scale run
    solo_notes.append({'note': root_note + 12 + scale[5], 'velocity': 85, 'length': 0.2, 'position': start_pos + 1.5})
    solo_notes.append({'note': root_note + 12 + scale[6], 'velocity': 90, 'length': 0.2, 'position': start_pos + 1.75})
    solo_notes.append({'note': root_note + 12 + scale[4], 'velocity': 95, 'length': 0.4, 'position': start_pos + 2.0})
    
    # 3. Ending phrase
    solo_notes.append({'note': root_note + 12 + scale[2], 'velocity': 80, 'length': 0.2, 'position': start_pos + 2.5})
    solo_notes.append({'note': root_note + 12 + scale[1], 'velocity': 85, 'length': 0.2, 'position': start_pos + 2.75})
    solo_notes.append({'note': root_note + 12, 'velocity': 110, 'length': 0.9, 'position': start_pos + 3.0})

    return solo_notes


@mcp.tool()
def generate_and_send_solo(chord_notes_str: str, start_beat: float = 0.0):
    """
    코드 노트를 입력받아 솔로 멜로디를 생성하고 FL Studio로 전송합니다.
    예: "60, 64, 67"
    """
    try:
        chord_notes = [int(n.strip()) for n in chord_notes_str.split(',')]
    except ValueError:
        return "Invalid chord format. Please provide comma-separated MIDI note numbers."

    root_note, chord_type = get_chord_details(chord_notes)

    if not root_note:
        return "Could not determine chord from the notes provided."

    print(f"Received chord: {chord_notes_str} -> Root: {root_note}, Type: {chord_type}")

    # 솔로 노트 생성
    solo_notes = generate_solo_notes(root_note, chord_type, start_beat)
    
    # FL Studio로 전송하기 위한 형식으로 변환
    notes_data_str = ""
    for note_info in solo_notes:
        notes_data_str += f"{note_info['note']},{note_info['velocity']},{note_info['length']},{note_info['position']}\n"
    
    print(f"Generated solo for {chord_type} chord rooted at {root_note}:")
    print(notes_data_str)

    # FL Studio로 멜로디 전송
    return send_melody(notes_data_str)


# --- MIDI Communication with FL Studio ---

def send_melody(notes_data: str):
    """
    노트 시퀀스를 FL Studio가 이해할 수 있는 MIDI 메시지로 변환하여 전송합니다.
    (기존 controller.py의 send_melody 함수와 거의 동일)
    """
    if not output_port:
        return "MIDI output port is not available."

    notes = []
    for line in notes_data.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.strip().split(',')
        if len(parts) != 4:
            continue
        try:
            notes.append((
                int(parts[0]), int(parts[1]), float(parts[2]), float(parts[3])
            ))
        except ValueError:
            continue
    
    if not notes:
        return "No valid notes to send."

    midi_data = []
    for note, velocity, length, position in notes:
        midi_data.extend([
            note, velocity,
            min(127, int(length)),
            int(round((length - int(length)) * 10)) % 10,
            min(127, int(position)),
            int(round((position - int(position)) * 10)) % 10
        ])
    
    # MIDI 전송 시작
    print(f"Transferring {len(notes)} solo notes to FL Studio...")
    
    # 1. 시작 신호 (note 0)
    send_midi_note(0)
    time.sleep(0.01)
    
    # 2. 총 노트 개수 전송
    send_midi_note(min(127, len(notes)))
    time.sleep(0.01)
    
    # 3. 실제 노트 데이터 전송
    for value in midi_data:
        send_midi_note(value)
        time.sleep(0.005) # 빠른 전송을 위해 sleep 시간 단축
    
    # 4. 종료 신호 (note 127)
    send_midi_note(127)

    return f"Successfully sent {len(notes)} notes to FL Studio."

def send_midi_note(note, velocity=1, duration=0.01):
    """Helper to send a single MIDI note on/off message."""
    if not output_port:
        return
    try:
        output_port.send(Message('note_on', note=note, velocity=velocity))
        time.sleep(duration)
        output_port.send(Message('note_off', note=note, velocity=0))
    except Exception as e:
        print(f"Error sending MIDI note: {e}")

# --- Background MIDI Listener ---

def midi_listener_thread():
    """
    FL Studio로부터 들어오는 MIDI 입력을 감지하는 백그라운드 스레드.
    코드를 감지하여 솔로 생성을 트리거합니다.
    """
    if not input_port:
        print("MIDI input port not available. Cannot listen for chords.")
        return

    print("MIDI listener started. Waiting for chords from FL Studio...")
    
    chord_buffer = []
    last_note_time = 0
    
    # 50ms 이내에 들어온 노트들을 하나의 코드로 간주
    CHORD_TIME_THRESHOLD = 0.05 

    while True:
        msg = input_port.receive()
        print(f"Received MIDI message: {msg}") # Add this line for debugging
        
        if msg.type == 'note_on' and msg.velocity > 0:
            current_time = time.time()
            
            # 이전 노트와 시간 간격이 크면, 이전 코드를 처리하고 버퍼를 리셋
            if chord_buffer and (current_time - last_note_time > CHORD_TIME_THRESHOLD):
                print(f"Chord detected: {chord_buffer}")
                chord_str = ", ".join(map(str, chord_buffer))
                generate_and_send_solo(chord_str)
                chord_buffer = []

            chord_buffer.append(msg.note)
            last_note_time = current_time
        
        # 짧은 시간 동안 아무 입력이 없으면 마지막 코드를 처리
        if chord_buffer and (time.time() - last_note_time > CHORD_TIME_THRESHOLD):
            print(f"Chord detected (by timeout): {chord_buffer}")
            chord_str = ", ".join(map(str, chord_buffer))
            generate_and_send_solo(chord_str)
            chord_buffer = []


# --- Main Execution ---

if __name__ == "__main__":
    if input_port:
        # MIDI 리스너를 데몬 스레드로 시작
        listener = threading.Thread(target=midi_listener_thread, daemon=True)
        listener.start()
    
    # FastMCP 서버 실행
    mcp.run(transport='stdio')
