"""
device_test.py
--------------
MIDI 출력 포트 연결 테스트.
- 특정 노트를 ON/OFF 전송하여 FL Studio에서 소리가 나는지 확인.
"""

import time
import mido
from mido import Message

# 🎛 MIDI 출력 포트 열기
# (FL Studio에서 동일한 포트를 인식하도록 설정해야 함)
output_port = mido.open_output('IAC ÎìúÎùºÏù¥Î≤Ñ loopMIDI Port 2')

# 🎹 테스트할 노트 (C3, MIDI 60)
msg_on = Message('note_on', note=60, velocity=64)   # 노트 켜기
msg_off = Message('note_off', note=60, velocity=64) # 노트 끄기

# 노트 ON → 1초 대기 → 노트 OFF
output_port.send(msg_on)
time.sleep(1)
output_port.send(msg_off)
