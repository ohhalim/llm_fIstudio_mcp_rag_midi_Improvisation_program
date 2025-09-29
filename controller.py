"""
controller.py
-------------
FL Studio를 Python에서 MIDI로 제어하기 위한 MCP 서버.
기능:
- Play / Stop / Tempo 변경
- 멜로디 전송
- MIDI 포트 목록 확인
"""

from typing import Any
import time
import mido
from mido import Message
from mcp.server.fastmcp import FastMCP

# 🎼 MCP 서버 초기화
mcp = FastMCP("flstudio")

# 🎛 FL Studio와 연결된 가상 MIDI 출력 포트 열기
# (loopMIDI 또는 IAC Driver 등에서 미리 생성된 포트 이름을 사용해야 함)
output_port = mido.open_output('IAC ÎìúÎùºÏù¥Î≤Ñ loopMIDI Port 2')


# 🎹 FL Studio 기능을 특정 MIDI 노트와 매핑
NOTE_PLAY = 60          # C3 → 재생
NOTE_STOP = 61          # C#3 → 정지
NOTE_RECORD = 62        # D3 → 녹음
NOTE_NEW_PROJECT = 63   # D#3 → 새 프로젝트
NOTE_SET_BPM = 64       # E3 → BPM 설정
NOTE_NEW_PATTERN = 65   # F3 → 새 패턴
NOTE_SELECT_PATTERN = 66  # F#3 → 패턴 선택
NOTE_ADD_CHANNEL = 67   # G3 → 채널 추가
NOTE_NAME_CHANNEL = 68  # G#3 → 채널 이름 지정
NOTE_ADD_NOTE = 69      # A3 → 노트 추가
NOTE_ADD_TO_PLAYLIST = 70  # A#3 → 플레이리스트 추가
NOTE_SET_PATTERN_LEN = 71  # B3 → 패턴 길이 설정
NOTE_CHANGE_TEMPO = 72     # C4 → 템포 변경 시작/종료


# 🎚 Custom MIDI CC (컨트롤 체인지) 매핑
CC_SELECT_CHANNEL = 100
CC_SELECT_STEP = 110
CC_TOGGLE_STEP = 111
CC_STEP_VELOCITY = 112


# 🥁 기본 드럼 노트 (표준 GM MIDI 매핑)
KICK = 36        # C1 → 킥
SNARE = 38       # D1 → 스네어
CLAP = 39        # D#1 → 클랩
CLOSED_HAT = 42  # F#1 → 하이햇 (닫힘)
OPEN_HAT = 46    # A#1 → 하이햇 (열림)


# ----------------------------------------------------
# 🛠 MCP 툴 (외부에서 호출 가능)
# ----------------------------------------------------

@mcp.tool()
def list_midi_ports():
    """시스템에 연결된 모든 MIDI 출력 포트 목록 반환"""
    return mido.get_output_names()


@mcp.tool()
def play():
    """재생 시작"""
    output_port.send(Message('note_on', note=NOTE_PLAY, velocity=127))
    output_port.send(Message('note_off', note=NOTE_PLAY, velocity=127))


@mcp.tool()
def stop():
    """재생 정지"""
    output_port.send(Message('note_on', note=NOTE_STOP, velocity=127))
    output_port.send(Message('note_off', note=NOTE_STOP, velocity=127))


# ----------------------------------------------------
# ⚙️ 보조 함수
# ----------------------------------------------------

def int_to_midi_bytes(value: int):
    """
    정수를 MIDI 전송 가능한 바이트 배열로 변환.
    (7비트 단위 분할)
    예: 999 → [7, 103]
    """
    result = []
    while value > 0:
        result.append(value & 0x7F)  # 7비트 추출
        value >>= 7
    return result or [0]


@mcp.tool()
def change_tempo(bpm: int):
    """
    FL Studio 템포 변경
    - NOTE_CHANGE_TEMPO(72) → 시작 신호
    - bpm 값을 바이트로 분해하여 note_on 메시지 전송
    - 73번 노트 → 종료 신호
    """
    bpm_bytes = int_to_midi_bytes(bpm)

    output_port.send(Message('note_on', note=NOTE_CHANGE_TEMPO, velocity=127))
    for b in bpm_bytes:
        output_port.send(Message('note_on', note=b, velocity=127))
    output_port.send(Message('note_on', note=73, velocity=127))


@mcp.tool()
def send_melody(notes_data: str):
    """
    멜로디 전송
    - 입력 형식: "note,velocity,length,pos\n..."
    - 예: "60,100,1.0,0.0\n62,120,0.5,1.0"
    """
    try:
        notes = []
        for line in notes_data.strip().splitlines():
            note, velocity, length, pos = map(float, line.split(','))
            # 정수 부분 / 소수점 부분 분리 (MIDI에서 처리하기 위함)
            length_whole, length_decimal = int(length), int((length % 1) * 100)
            pos_whole, pos_decimal = int(pos), int((pos % 1) * 100)

            notes.append([int(note), int(velocity), length_whole, length_decimal, pos_whole, pos_decimal])

        # 메시지 전송
        for note in notes:
            for val in note:
                output_port.send(Message('note_on', note=val, velocity=127))

        return f"Sent melody with {len(notes)} notes."

    except Exception as e:
        return f"Error sending melody: {e}"


@mcp.tool()
def send_midi_note(note: int, velocity: int = 100, duration: float = 0.1):
    """
    단일 MIDI 노트 전송
    - note: MIDI 노트 번호
    - velocity: 건반 세기 (0~127)
    - duration: 노트 지속 시간 (초)
    """
    output_port.send(Message('note_on', note=note, velocity=velocity))
    time.sleep(duration)
    output_port.send(Message('note_off', note=note, velocity=velocity))


# ----------------------------------------------------
# 🚀 실행부
# ----------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport='stdio')
