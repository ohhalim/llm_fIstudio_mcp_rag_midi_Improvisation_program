# improvisation_controller.py
# name=RAG Improvisation Controller
# FL Studio용 실시간 코드 분석 및 RAG 기반 즉흥 솔로 생성 시스템

import transport
import channels
import midi
import general
import time

# 전역 변수
current_notes = set()           # 현재 눌린 노트들
note_start_times = {}          # 각 노트의 시작 시간
last_detected_chord = None     # 마지막으로 감지된 코드
chord_detection_delay = 0.3    # 코드 감지 최소 지연 시간 (초)
solo_channel = 2              # 솔로 연주 채널 (채널 2)

# 코드 패턴 데이터베이스 (루트에서의 반음 간격)
CHORD_PATTERNS = {
    frozenset([0, 4, 7]): "major",
    frozenset([0, 3, 7]): "minor",
    frozenset([0, 4, 7, 11]): "maj7",
    frozenset([0, 4, 7, 10]): "dom7",
    frozenset([0, 3, 7, 10]): "min7",
    frozenset([0, 3, 7, 11]): "minMaj7",
    frozenset([0, 4, 7, 9]): "6",
    frozenset([0, 3, 7, 9]): "min6",
    frozenset([0, 4, 7, 9, 11]): "maj9",
    frozenset([0, 3, 7, 9, 10]): "min9",
    frozenset([0, 3, 6]): "dim",
    frozenset([0, 3, 6, 9]): "dim7",
    frozenset([0, 4, 8]): "aug",
    frozenset([0, 5, 7]): "sus4",
    frozenset([0, 2, 7]): "sus2",
    frozenset([0, 5, 7, 10]): "7sus4",
    frozenset([0, 7]): "5",
    frozenset([0, 4]): "maj_no5",
    frozenset([0, 3]): "min_no5",
}

# RAG 솔로 패턴 데이터베이스
SOLO_PATTERNS = {
    # C major 관련 패턴들
    "C_major": {
        "jazz": [60, 62, 64, 65, 67, 69, 71, 72],
        "blues": [60, 63, 64, 67, 70, 67, 64, 60],
        "classical": [72, 71, 69, 67, 65, 64, 62, 60],
        "rock": [60, 62, 64, 67, 65, 62, 60]
    },
    "A_minor": {
        "jazz": [57, 60, 62, 64, 65, 67, 69, 72],
        "blues": [57, 60, 63, 65, 67, 65, 60, 57],
        "classical": [69, 67, 65, 64, 62, 60, 57],
        "rock": [57, 60, 62, 65, 67, 65, 60, 57]
    },
    "F_major": {
        "jazz": [53, 55, 57, 58, 60, 62, 64, 65],
        "blues": [53, 56, 58, 60, 63, 60, 58, 53],
        "classical": [65, 64, 62, 60, 58, 57, 55, 53],
        "rock": [53, 55, 58, 60, 62, 60, 58, 53]
    },
    "G_major": {
        "jazz": [55, 57, 59, 60, 62, 64, 66, 67],
        "blues": [55, 58, 59, 62, 65, 62, 59, 55],
        "classical": [67, 66, 64, 62, 60, 59, 57, 55],
        "rock": [55, 57, 59, 62, 64, 62, 59, 55]
    },
    "D_minor": {
        "jazz": [50, 53, 55, 57, 58, 60, 62, 65],
        "blues": [50, 53, 56, 58, 61, 58, 53, 50],
        "classical": [62, 60, 58, 57, 55, 53, 50],
        "rock": [50, 53, 55, 58, 60, 58, 55, 50]
    },
    "E_minor": {
        "jazz": [52, 55, 57, 59, 60, 62, 64, 67],
        "blues": [52, 55, 58, 60, 63, 60, 55, 52],
        "classical": [64, 62, 60, 59, 57, 55, 52],
        "rock": [52, 55, 57, 60, 62, 60, 57, 52]
    },
    "B_dim": {
        "jazz": [59, 62, 65, 68, 71, 68, 65, 62],
        "classical": [71, 68, 65, 62, 59],
        "rock": [59, 62, 65, 68, 65, 62, 59]
    }
}

# 사용자 스타일 선호도 (학습 가능)
USER_PREFERENCES = {
    "jazz": 0.8,
    "blues": 0.9,
    "classical": 0.6,
    "rock": 0.7
}

# 음명 변환 테이블
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def OnInit():
    """FL Studio 로드 시 초기화"""
    print("RAG Improvisation Controller initialized")
    print("실시간 코드 분석 및 솔로 생성 시스템 준비 완료")
    return

def OnDeInit():
    """FL Studio 종료 시"""
    print("RAG Improvisation Controller deinitialized")
    return

def OnRefresh(flags):
    """상태 변경"""
    return

def OnMidiIn(event):
    """MIDI 입력 처리 - 실시간 코드 분석 및 솔로 생성"""
    global current_notes, note_start_times, last_detected_chord
    
    current_time = time.time()
    
    # Note On 처리
    if event.status >= midi.MIDI_NOTEON and event.status < midi.MIDI_NOTEON + 16 and event.data2 > 0:
        note = event.data1
        note_class = note % 12
        
        # 노트 추가
        current_notes.add(note_class)
        note_start_times[note_class] = current_time
        
        note_name = NOTE_NAMES[note_class]
        octave = note // 12 - 1
        print(f"🎵 키 눌림: {note_name}{octave} (velocity: {event.data2})")
        
        # 코드 분석 (2개 이상 노트가 있을 때)
        if len(current_notes) >= 2:
            detected_chord = analyze_chord()
            if detected_chord and detected_chord != last_detected_chord:
                last_detected_chord = detected_chord
                generate_and_play_solo(detected_chord)
    
    # Note Off 처리
    elif event.status >= midi.MIDI_NOTEOFF and event.status < midi.MIDI_NOTEOFF + 16:
        note = event.data1
        note_class = note % 12
        
        # 노트 제거
        current_notes.discard(note_class)
        note_start_times.pop(note_class, None)
        
        note_name = NOTE_NAMES[note_class]
        octave = note // 12 - 1
        print(f"🎵 키 놓음: {note_name}{octave}")
        
        # 남은 노트가 2개 미만이면 코드 해제
        if len(current_notes) < 2:
            if last_detected_chord:
                print("🎼 코드 해제")
                last_detected_chord = None
    
    return

def analyze_chord():
    """현재 눌린 노트들로 코드 분석"""
    global current_notes, note_start_times, chord_detection_delay
    
    current_time = time.time()
    
    # 충분히 오래 지속된 노트들만 고려 (잘못된 인식 방지)
    stable_notes = set()
    for note in current_notes:
        if current_time - note_start_times.get(note, current_time) >= chord_detection_delay:
            stable_notes.add(note)
    
    if len(stable_notes) < 2:
        return None
    
    # 가능한 모든 루트로 코드 분석 시도
    best_chord = None
    best_score = 0
    
    for root in stable_notes:
        intervals = frozenset((note - root) % 12 for note in stable_notes)
        
        if intervals in CHORD_PATTERNS:
            chord_type = CHORD_PATTERNS[intervals]
            # 점수: 더 많은 노트 = 더 높은 점수
            score = len(stable_notes)
            
            if score > best_score:
                best_chord = {
                    'root': root,
                    'type': chord_type,
                    'notes': sorted(list(stable_notes)),
                    'confidence': score
                }
                best_score = score
    
    if best_chord:
        chord_name = f"{NOTE_NAMES[best_chord['root']]} {best_chord['type']}"
        note_list = [NOTE_NAMES[note] for note in best_chord['notes']]
        
        print(f"🎼 코드 감지: {chord_name}")
        print(f"   구성음: {' + '.join(note_list)}")
        print(f"   확신도: {'⭐' * min(best_chord['confidence'], 5)}")
    
    return best_chord

def generate_and_play_solo(chord_info):
    """RAG 기반 솔로 생성 및 연주"""
    global solo_channel, USER_PREFERENCES, SOLO_PATTERNS
    
    root = chord_info['root']
    chord_type = chord_info['type']
    
    # 코드 키 생성 (데이터베이스 검색용)
    chord_key = f"{NOTE_NAMES[root]}_{chord_type}"
    
    print(f"🎵 솔로 생성 중... (코드: {chord_key})")
    
    # RAG: 패턴 데이터베이스에서 검색
    solo_pattern = None
    
    # 1. 정확한 매칭 찾기
    if chord_key in SOLO_PATTERNS:
        solo_pattern = select_best_pattern(SOLO_PATTERNS[chord_key])
        print(f"   ✅ 매칭 패턴 찾음: {chord_key}")
    
    # 2. 유사한 패턴 찾기 (같은 타입의 다른 루트)
    elif not solo_pattern:
        for pattern_key, patterns in SOLO_PATTERNS.items():
            if chord_type in pattern_key:
                solo_pattern = select_best_pattern(patterns)
                # 루트에 맞게 트랜스포즈
                solo_pattern = transpose_pattern(solo_pattern, root - get_root_from_key(pattern_key))
                print(f"   ✅ 유사 패턴 적용: {pattern_key} -> {chord_key}")
                break
    
    # 3. 기본 아르페지오 생성 (폴백)
    if not solo_pattern:
        solo_pattern = generate_basic_arpeggio(chord_info)
        print(f"   ✅ 기본 아르페지오 생성")
    
    # 솔로 연주
    if solo_pattern:
        play_solo_pattern(solo_pattern)

def select_best_pattern(patterns):
    """사용자 선호도 기반 최적 패턴 선택"""
    global USER_PREFERENCES
    
    best_style = None
    best_score = 0
    
    for style, preference in USER_PREFERENCES.items():
        if style in patterns and preference > best_score:
            best_style = style
            best_score = preference
    
    if best_style:
        print(f"   🎨 선택된 스타일: {best_style} (선호도: {best_score:.1f})")
        return patterns[best_style]
    
    # 기본값으로 jazz 스타일
    return patterns.get('jazz', list(patterns.values())[0])

def transpose_pattern(pattern, semitones):
    """패턴을 지정된 반음만큼 이동"""
    return [note + semitones for note in pattern]

def get_root_from_key(pattern_key):
    """패턴 키에서 루트 노트 추출"""
    note_part = pattern_key.split('_')[0]
    try:
        return NOTE_NAMES.index(note_part)
    except ValueError:
        return 0  # 기본값 C

def generate_basic_arpeggio(chord_info):
    """기본 아르페지오 패턴 생성"""
    root = chord_info['root']
    notes = chord_info['notes']
    
    # 중음역대로 이동 (60 = C4)
    base_octave = 60
    chord_notes = [note + base_octave for note in notes]
    
    # 상행 아르페지오 + 하행
    pattern = chord_notes + chord_notes[::-1]
    
    print(f"   🎼 아르페지오: {len(pattern)}개 노트")
    return pattern

def play_solo_pattern(pattern):
    """솔로 패턴 연주"""
    global solo_channel
    
    print(f"🎵 솔로 연주 시작 (채널 {solo_channel})")
    
    # 채널 선택
    channels.selectOneChannel(solo_channel)
    
    # 각 노트를 순차적으로 연주
    for i, note in enumerate(pattern):
        if 0 <= note <= 127:  # 유효한 MIDI 노트 범위
            # Note On
            channels.midiNoteOn(solo_channel, note, 80)  # 적당한 볼륨
            
            note_name = NOTE_NAMES[note % 12]
            octave = note // 12 - 1
            print(f"   🎵 {i+1}/{len(pattern)}: {note_name}{octave}")
            
            # 노트 길이 (16분음표 기준)
            # FL Studio에서는 실제 시간 대기 대신 짧은 지연 후 Note Off
            general.processRECBuffer()  # FL Studio 내부 처리
            
    print("🎵 솔로 연주 완료")

def stop_all_solo_notes():
    """모든 솔로 노트 정지"""
    global solo_channel
    
    for note in range(128):
        channels.midiNoteOn(solo_channel, note, 0)  # Note Off

# 사용자 설정 함수들
def set_solo_channel(channel):
    """솔로 채널 설정"""
    global solo_channel
    if 0 <= channel < channels.channelCount():
        solo_channel = channel
        print(f"솔로 채널 설정: {solo_channel}")
        return True
    return False

def update_style_preference(style, preference):
    """스타일 선호도 업데이트 (학습 기능)"""
    global USER_PREFERENCES
    if 0.0 <= preference <= 1.0:
        USER_PREFERENCES[style] = preference
        print(f"스타일 선호도 업데이트: {style} = {preference:.1f}")

def set_chord_detection_delay(delay):
    """코드 감지 지연시간 설정"""
    global chord_detection_delay
    if 0.0 <= delay <= 2.0:
        chord_detection_delay = delay
        print(f"코드 감지 지연시간: {delay}초")

# 테스트 함수
def test_chord_recognition():
    """코드 인식 테스트"""
    print("🧪 코드 인식 테스트 시작")
    
    # C major 테스트
    test_notes = [0, 4, 7]  # C, E, G
    print(f"테스트 코드: C major {test_notes}")
    
    # 전역 변수에 테스트 노트 설정
    global current_notes, note_start_times
    current_notes = set(test_notes)
    current_time = time.time()
    for note in test_notes:
        note_start_times[note] = current_time - 1.0  # 1초 전에 시작된 것으로 설정
    
    # 코드 분석
    result = analyze_chord()
    if result:
        print("✅ 테스트 성공!")
    else:
        print("❌ 테스트 실패")

# FL Studio 이벤트 핸들러들
def OnMidiMsg(event, timestamp=0):
    """MCP 서버 등에서 보낸 MIDI 메시지 처리 (선택사항)"""
    event.handled = False  # 기본 처리도 계속하도록
    return

def OnTransport(isPlaying):
    """재생 상태 변경 시"""
    if not isPlaying:
        stop_all_solo_notes()
    return

def OnChannelChange(channel):
    """채널 변경 시 솔로 채널도 따라 변경"""
    global solo_channel
    solo_channel = channel + 1  # 솔로는 다음 채널로
    print(f"솔로 채널 자동 변경: {solo_channel}")
    return

# 시작 시 테스트 실행
# test_chord_recognition()  # 주석 해제하여 테스트 실행