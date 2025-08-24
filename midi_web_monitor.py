#!/usr/bin/env python3
"""
웹 기반 MIDI 모니터
브라우저에서 실시간으로 MIDI 연주를 확인할 수 있습니다.
"""

from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import rtmidi
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'midi-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# MIDI 입력 설정
midi_in = rtmidi.MidiIn()
midi_connected = False
monitoring = False

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎹 MIDI 키보드 모니터</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .title {
            text-align: center;
            font-size: 2em;
            margin-bottom: 20px;
        }
        .status {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .midi-log {
            background: #000;
            padding: 15px;
            border-radius: 5px;
            height: 400px;
            overflow-y: scroll;
            font-family: monospace;
        }
        .note-on {
            color: #00ff00;
            font-weight: bold;
        }
        .note-off {
            color: #ff6666;
        }
        .control {
            color: #66ccff;
        }
        button {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="title">🎹 실시간 MIDI 키보드 모니터</div>
        
        <div class="status">
            <div>연결 상태: <span id="connection-status">연결 중...</span></div>
            <div>모니터링: <span id="monitoring-status">준비 중</span></div>
            <div>총 메시지: <span id="message-count">0</span></div>
        </div>
        
        <button onclick="startMonitoring()">🎵 모니터링 시작</button>
        <button onclick="stopMonitoring()">⏹️ 모니터링 중지</button>
        <button onclick="clearLog()">🗑️ 로그 지우기</button>
        
        <div class="midi-log" id="midi-log">
            <div>🎹 MIDI 키보드를 연주해보세요!</div>
        </div>
    </div>

    <script>
        const socket = io();
        let messageCount = 0;
        
        socket.on('connect', function() {
            document.getElementById('connection-status').textContent = '✅ 연결됨';
        });
        
        socket.on('disconnect', function() {
            document.getElementById('connection-status').textContent = '❌ 연결 끊김';
        });
        
        socket.on('midi_message', function(data) {
            messageCount++;
            document.getElementById('message-count').textContent = messageCount;
            
            const log = document.getElementById('midi-log');
            const message = document.createElement('div');
            
            const timestamp = new Date().toLocaleTimeString();
            
            if (data.type === 'note_on') {
                message.className = 'note-on';
                message.innerHTML = `🎵 [${timestamp}] 키 눌림: ${data.note} (세기: ${data.velocity})`;
            } else if (data.type === 'note_off') {
                message.className = 'note-off';
                message.innerHTML = `🎵 [${timestamp}] 키 놓음: ${data.note}`;
            } else if (data.type === 'control') {
                message.className = 'control';
                message.innerHTML = `🎛️ [${timestamp}] 컨트롤: CC${data.controller} = ${data.value}`;
            }
            
            log.appendChild(message);
            log.scrollTop = log.scrollHeight;
        });
        
        socket.on('monitoring_status', function(data) {
            document.getElementById('monitoring-status').textContent = 
                data.status ? '🟢 모니터링 중' : '🔴 정지됨';
        });
        
        function startMonitoring() {
            socket.emit('start_monitoring');
        }
        
        function stopMonitoring() {
            socket.emit('stop_monitoring');
        }
        
        function clearLog() {
            document.getElementById('midi-log').innerHTML = 
                '<div>🎹 MIDI 키보드를 연주해보세요!</div>';
            messageCount = 0;
            document.getElementById('message-count').textContent = '0';
        }
    </script>
</body>
</html>
'''

def get_note_name(note_number):
    """MIDI 노트 번호를 음표 이름으로 변환"""
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = note_number // 12 - 1
    note_name = note_names[note_number % 12]
    return f"{note_name}{octave}"

def midi_listener():
    """MIDI 메시지를 지속적으로 감지하는 함수"""
    global monitoring
    
    while True:
        if monitoring and midi_connected:
            msg = midi_in.get_message()
            
            if msg:
                message, deltatime = msg
                
                if len(message) >= 3:
                    status = message[0]
                    data1 = message[1]
                    data2 = message[2]
                    
                    # Note On
                    if status >= 144 and status <= 159 and data2 > 0:
                        note_name = get_note_name(data1)
                        socketio.emit('midi_message', {
                            'type': 'note_on',
                            'note': note_name,
                            'velocity': data2
                        })
                    
                    # Note Off
                    elif (status >= 128 and status <= 143) or (status >= 144 and status <= 159 and data2 == 0):
                        note_name = get_note_name(data1)
                        socketio.emit('midi_message', {
                            'type': 'note_off',
                            'note': note_name
                        })
                    
                    # Control Change
                    elif status >= 176 and status <= 191:
                        socketio.emit('midi_message', {
                            'type': 'control',
                            'controller': data1,
                            'value': data2
                        })
        
        time.sleep(0.001)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('start_monitoring')
def start_monitoring():
    global midi_connected, monitoring
    
    ports = midi_in.get_ports()
    
    # Keystation 찾기
    keystation_port = -1
    for i, port in enumerate(ports):
        if "Keystation" in port and "USB MIDI" in port:
            keystation_port = i
            break
    
    if keystation_port != -1:
        try:
            if not midi_connected:
                midi_in.open_port(keystation_port)
                midi_connected = True
            
            monitoring = True
            emit('monitoring_status', {'status': True})
            
            print(f"🎹 MIDI 모니터링 시작: {ports[keystation_port]}")
            
        except Exception as e:
            print(f"❌ MIDI 연결 실패: {e}")
            emit('monitoring_status', {'status': False})
    else:
        print("❌ Keystation을 찾을 수 없습니다.")
        emit('monitoring_status', {'status': False})

@socketio.on('stop_monitoring')
def stop_monitoring():
    global monitoring
    monitoring = False
    emit('monitoring_status', {'status': False})
    print("⏹️ MIDI 모니터링 중지")

if __name__ == '__main__':
    # MIDI 리스너 스레드 시작
    midi_thread = threading.Thread(target=midi_listener, daemon=True)
    midi_thread.start()
    
    print("🌐 웹 서버 시작 중...")
    print("📱 브라우저에서 http://localhost:5000 으로 접속하세요!")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)