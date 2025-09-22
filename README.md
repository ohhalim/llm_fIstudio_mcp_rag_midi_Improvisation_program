# FL Studio AI 솔로 생성기

이 프로젝트는 FL Studio에서 코드를 연주하면 AI가 실시간으로 어울리는 솔로 라인을 생성하여 DAW로 다시 보내주는 시스템입니다.

Python으로 작성된 MCP 서버(`controller.py`)가 미디 코드를 입력받아 멜로디를 생성하고, FL Studio 내부의 미디 스크립트(`device_test.py`)가 생성된 멜로디를 받아 피아노 롤에 녹음하는 방식으로 동작합니다.

## 작동 방식

1.  **FL Studio 설정**: FL Studio의 'MIDI Out' 플러그인을 사용하여 연주하는 코드를 특정 가상 미디 포트(`loopMIDI Port 3`)로 보냅니다.
2.  **컨트롤러 서버**: `controller.py` 스크립트가 이 포트를 리스닝하고 있다가 코드가 감지되면 음악적 속성(루트 음, 메이저/마이너 등)을 분석합니다.
3.  **AI 솔로 생성**: 분석된 코드를 기반으로, 서버는 아르페지오와 스케일 연주를 조합하여 간단한 솔로 라인을 생성합니다.
4.  **FL Studio로 전송**: 생성된 솔로는 특수한 미디 메시지 시퀀스로 포맷되어 다른 가상 미디 포트(`loopMIDI Port 2`)로 전송됩니다.
5.  **FL Studio 스크립트**: FL Studio 내에서 실행 중인 `device_test.py` 스크립트가 `loopMIDI Port 2`를 리스닝하다가 메시지 시퀀스를 해독하여 선택된 채널의 피아노 롤에 노트를 직접 녹음합니다.

## 요구사항

-   Python 3.8 이상
-   FL Studio
-   가상 미디 포트 프로그램 (예: Windows용 [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)). macOS에서는 내장된 'Audio MIDI 설정'을 사용할 수 있습니다.
-   Python 라이브러리: `mido`, `python-rtmidi`, `fastmcp`, `httpx`

## 1. 설정

### 1단계: Python 의존성 설치

```bash
pip install mido python-rtmidi "fastmcp[cli]" httpx
```

### 2단계: 가상 미디 포트 설정

FL Studio와 Python 스크립트 간의 통신을 위해 두 개의 가상 미디 포트가 필요합니다.

-   **Windows (loopMIDI 사용 시):**
    1.  loopMIDI를 엽니다.
    2.  `+` 버튼을 두 번 클릭하여 두 개의 포트를 생성합니다.
    3.  포트 이름을 다음과 같이 변경합니다:
        -   `loopMIDI Port 2`
        -   `   `

-   **macOS (Audio MIDI 설정 사용 시):**
    1.  'Audio MIDI 설정'을 엽니다 (Spotlight에서 검색 가능).
    2.  `윈도우 > MIDI 스튜디오 보기`로 이동합니다.
    3.  'IAC 드라이버' 아이콘을 더블 클릭합니다.
    4.  '기기가 온라인입니다'가 체크되어 있는지 확인합니다.
    5.  '포트' 섹션에서 `+` 버튼을 눌러 두 개의 포트를 생성하고, 스크립트와의 일관성을 위해 이름을 `loopMIDI Port 2`와 `loopMIDI Port 3`로 변경합니다 (이름을 더블 클릭하여 수정).

### 3단계: FL Studio 설정

1.  **컨트롤러 스크립트 연결 (`device_test.py`):**
    -   `Options > MIDI Settings`로 이동합니다.
    -   `Input` 섹션에서 `loopMIDI Port 2`를 찾습니다.
    -   선택한 후 'Controller type' 드롭다운 메뉴에서 `Test Controller` 스크립트를 선택합니다 (`device_test.py` 파일에 정의된 이름).
    -   **중요**: 여기서 할당된 포트가 `controller.py`의 `OUTPUT_PORT_NAME`과 일치하는지 확인하세요.

2.  **코드 입력 채널 설정:**
    -   프로젝트에 새 채널을 추가합니다 (예: 'Fruity Keyboard Controller' 또는 원하는 악기).
    -   새 채널을 클릭하여 채널 설정 창을 엽니다.
    -   이 채널에 **'MIDI Out'** 플러그인을 추가합니다.
    -   'MIDI Out' 플러그인 설정에서:
        -   **Port**를 `3`으로 설정합니다. 이는 `loopMIDI Port 3`에 해당합니다.
        -   **Channel**은 `1`로 설정합니다 (이 설정에서는 크게 중요하지 않습니다).

## 2. 사용법

1.  **컨트롤러 서버 실행:**
    -   터미널 또는 명령 프롬프트를 엽니다.
    -   프로젝트 디렉토리로 이동합니다.
    -   다음 명령어로 스크립트를 실행합니다:
        ```bash
        python controller.py
        ```
    -   미디 포트가 성공적으로 열리고 리스너가 실행 중이라는 메시지가 표시되어야 합니다.

2.  **FL Studio에서 솔로를 녹음할 채널 선택:**
    -   FL Studio에서 생성된 솔로가 녹음되기를 원하는 채널(예: 피아노, 신디사이저 등)을 선택합니다. 이 채널이 `device_test.py` 스크립트가 제어할 대상입니다.

3.  **코드 연주:**
    -   **'MIDI Out'** 플러그인이 있는 채널의 피아노 롤로 이동합니다.
    -   코드를 연주하거나 그립니다 (예: C Major: C4, E4, G4).

4.  **결과 확인!**
    -   `controller.py`를 실행 중인 터미널에 감지된 코드가 출력됩니다.
    -   거의 즉시, 2단계에서 선택했던 **대상 채널**의 피아노 롤에 새로운 솔로 멜로디가 녹음됩니다.

이제 'MIDI Out' 채널에서 코드 진행을 연주하면, 악기 채널에서 AI가 계속해서 솔로 라인을 생성하는 것을 확인할 수 있습니다!