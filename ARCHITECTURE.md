# LLM 기반 실시간 MIDI 즉흥 연주 시스템 아키텍처

## 1. 시스템 개요

본 문서는 LLM과 RAG(Retrieval-Augmented Generation) 기술을 활용한 실시간 MIDI 즉흥 연주 시스템의 아키텍처를 정의합니다. 사용자가 외부 MIDI 키보드로 화성 코드를 입력하면, 시스템은 해당 코드에 어울리는 멜로디나 연주 패턴을 LLM을 통해 생성하여 FL Studio와 같은 DAW(Digital Audio Workstation)로 출력합니다. 이 과정에서 RAG 시스템은 LLM이 더 음악적인 맥락에 맞는 결과를 생성할 수 있도록 관련 MIDI 데이터를 참조 정보로 제공합니다.

## 2. 핵심 기능

- **실시간 MIDI 입력**: 외부 MIDI 키보드에서 연주하는 화성 코드 신호를 실시간으로 수신합니다.
- **RAG 기반 컨텍스트 제공**: 입력된 화성 코드와 가장 관련성 높은 MIDI 데이터 샘플을 Vector Store에서 검색하여 LLM에 컨텍스트로 제공합니다.
- **LLM을 통한 MIDI 생성**: Ollama를 통해 로컬에서 실행되는 Qwen 모델이 입력된 코드와 RAG 컨텍스트를 기반으로 새로운 MIDI 시퀀스를 생성합니다.
- **DAW 연동 출력**: 생성된 MIDI 데이터를 MCP(Master Control Program) 서버를 통해 FL Studio로 전송하여 실시간으로 연주합니다.

## 3. 시스템 아키텍처

본 시스템은 각 기능별로 분리된 마이크로서비스 아키텍처(MSA)를 따릅니다. `docker-compose`를 통해 각 서비스의 독립적인 실행 및 확장을 보장합니다.

### 3.1. 아키텍처 다이어그램

```
+-------------------+      (1) MIDI Chord      +-----------------+      (2) Chord Info      +---------------------+
| External Keyboard | ----------------------> |   MIDI Service  | ---------------------> | Gateway (MCP) Server|
+-------------------+                         +-----------------+                        +----------+----------+
        /|\                                                                                         |
         | (9) Playback                                                                             |
         |                                                                                          |
+-------------------+      (8) Generated MIDI    +-----------------+                        +-------+-------+
|    FL Studio      | <---------------------- |   MIDI Service  | <--------------------- | RAG Service |
+-------------------+      (7) Send to DAW     +-----------------+      (6) LLM Result      +---------------+                                                                                                    /|\
                                                                                                    |
                                                                                           +--------+--------+
                                                                                           |  Vector Store   |
                                                                                           +-----------------+
                                                                                                    |
                                                                                                    |
                                                                                           +--------+--------+
                                                                                           |  Ollama (Qwen)  |
                                                                                           +-----------------+
```

### 3.2. 컴포넌트 상세

#### 1. MIDI Service (`midi-service`)
- **역할**:
    - 외부 MIDI 장치로부터 들어오는 MIDI 신호를 수신하고 파싱하여 화성 코드 등의 정보로 변환합니다. (Input)
    - Gateway로부터 생성된 MIDI 데이터를 받아 FL Studio가 인식할 수 있는 가상 MIDI 포트로 출력합니다. (Output)
- **주요 기술**: Python, `mido` or `rtmidi-python`, FastAPI

#### 2. RAG Service (`rag-service`)
- **역할**:
    - Gateway로부터 화성 코드 정보를 받습니다.
    - 사전에 학습/임베딩된 MIDI 데이터가 저장된 Vector Store에서 해당 코드와 가장 유사하거나 연관성 높은 MIDI 샘플들을 검색합니다.
    - 검색된 MIDI 샘플(컨텍스트)을 Gateway로 반환합니다.
- **주요 기술**: Python, LangChain/LlamaIndex, FAISS/ChromaDB, FastAPI

#### 3. Gateway (MCP) Server (`gateway`)
- **역할**:
    - 전체 시스템의 요청 흐름을 제어하는 중앙 컨트롤 타워 역할을 합니다.
    - `MIDI Service`에서 코드 정보를 받아 `RAG Service`에 컨텍스트를 요청합니다.
    - `RAG Service`에서 받은 컨텍스트와 원본 코드 정보를 조합하여 Ollama의 Qwen 모델에 전달할 프롬프트를 생성합니다.
    - Ollama로부터 생성된 MIDI 데이터를 받아 `MIDI Service`에 전송하여 최종 출력을 요청합니다.
- **주요 기술**: Python, FastAPI, HTTPX/AIOHTTP

#### 4. Ollama (Qwen LLM)
- **역할**:
    - Gateway로부터 받은 프롬프트(화성 코드 + RAG 컨텍스트)를 기반으로 새로운 MIDI 시퀀스를 텍스트 형태(예: JSON, ABC 표기법)로 생성합니다.
    - 로컬 환경에서 독립적으로 실행됩니다.
- **주요 기술**: Ollama, Qwen

#### 5. User Service & Database (`user-service`, `infrastructure/init.sql`)
- **역할**:
    - (선택 확장) 사용자 계정, 생성된 MIDI 히스토리, 설정 등을 관리합니다.
    - PostgreSQL 데이터베이스를 사용하여 데이터를 영구 저장합니다.
- **주요 기술**: Python, FastAPI, SQLAlchemy, PostgreSQL

## 4. 데이터 흐름 (End-to-End Flow)

1.  **입력**: 사용자가 외부 MIDI 키보드로 C Major 7 코드를 연주합니다.
2.  **캡처**: `MIDI Service`가 MIDI 신호를 캡처하고, "CM7"이라는 코드 정보와 함께 JSON 형태로 `Gateway`에 전송합니다.
3.  **컨텍스트 요청**: `Gateway`는 "CM7" 정보를 `RAG Service`에 전달하여 관련 컨텍스트를 요청합니다.
4.  **검색**: `RAG Service`는 Vector Store에서 "CM7"과 관련된 MIDI 패턴(예: CM7 아르페지오, 어울리는 멜로디 라인)을 검색합니다.
5.  **프롬프트 생성**: `Gateway`는 검색된 MIDI 패턴을 텍스트로 변환하고, "CM7 코드에 어울리는 4마디 멜로디를 생성해줘. 참고할만한 패턴은 다음과 같아: [검색된 MIDI 패턴]"과 같은 프롬프트를 만듭니다.
6.  **LLM 추론**: `Gateway`가 이 프롬프트를 Ollama API를 통해 Qwen 모델에 전송합니다. Qwen 모델은 새로운 MIDI 멜로디를 나타내는 텍스트(예: `["C5", "E5", "G5", "B5", ...]`)
를 생성하여 반환합니다.
7.  **결과 전송**: `Gateway`는 LLM의 결과물을 `MIDI Service`에 전달합니다.
8.  **MIDI 변환 및 출력**: `MIDI Service`는 수신한 텍스트를 실제 MIDI 메시지로 변환하여 FL Studio가 리스닝하고 있는 가상 MIDI 포트로 전송합니다.
9.  **재생**: FL Studio는 수신한 MIDI 신호를 통해 악기 소리를 재생합니다.

## 5. 구현을 위한 제안

- **MIDI I/O**: `MIDI Service`에서 MIDI 입출력을 위해 Python의 `mido` 라이브러리를 활용하고, FL Studio와의 연동을 위해 `loopMIDI` (Windows)나 macOS의 `IAC Driver` (Audio MIDI Setup) 같은 가상 MIDI 포트 설정이 필요합니다.
- **데이터 표현**: 시스템 전체에서 MIDI 데이터를 일관된 형식으로 다루는 것이 중요합니다. MIDI 노트를 `{ "note": "C5", "velocity": 100, "duration": 0.5 }` 와 같은 JSON 객체의 배열로 표현하는 방식을 추천합니다.
- **RAG 데이터 구축**: `RAG Service`의 Vector Store를 구축하기 위해, 다양한 장르와 스타일의 MIDI 파일을 수집하고, 코드별/마디별로 의미 있는 단위로 분할하여 임베딩하는 전처리 파이프라인이 필요합니다.


mcp 없이도 api로 연결해서 쓰면 되잖아 
그래서 올라마로 돌리면 되고 
뭐가 중요할까???

그럼 
ollama qwen으로 돌리고
midi 데이터 rag 하는 코드파일
llm과 flstudio 소통 코드 파일
외부 키보드 인풋 만드는 코드 파일 
