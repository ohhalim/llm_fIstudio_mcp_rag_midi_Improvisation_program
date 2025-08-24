# FL Studio RAG 즉흥 연주 시스템 설치 및 테스트 가이드

## 🎯 완성된 시스템 개요

**RAG 기반 실시간 즉흥 연주 시스템**이 완성되었습니다!

### ✨ 주요 기능
1. **실시간 코드 인식**: MIDI 키보드 입력을 실시간으로 코드로 분석
2. **RAG 솔로 생성**: 감지된 코드에 맞는 개인화된 솔로 라인 생성  
3. **스타일별 패턴**: Jazz, Blues, Classical, Rock 스타일별 솔로 패턴
4. **사용자 학습**: 개인 선호도를 학습하여 점점 더 개인화된 솔로 생성
5. **FL Studio 완벽 연동**: FL Studio 내에서 바로 솔로 재생

## 🚀 설치 방법

### 1단계: 스크립트 파일 복사
```bash
# FL Studio Scripts 폴더로 이동 (Windows)
C:\Users\[사용자명]\Documents\Image-Line\FL Studio\Settings\Hardware

# FL Studio Scripts 폴더로 이동 (macOS) 
/Applications/FL Studio 21.app/Contents/Resources/FL/Scripts

# improvisation_controller.py 파일을 해당 폴더에 복사
```

### 2단계: FL Studio에서 스크립트 활성화
1. FL Studio 실행
2. **Options** → **MIDI Settings** 
3. **Input** 탭에서 Keystation 88 MK3 선택
4. **Controller type**을 `improvisation_controller.py`로 설정
5. **Enable** 체크박스 활성화

### 3단계: 솔로 채널 설정
1. FL Studio Mixer에서 **채널 2**를 솔로 전용으로 설정
2. 원하는 악기/신스를 채널 2에 로드 (예: Piano, Synth Lead 등)

## 🧪 테스트 방법

### 기본 테스트
1. **FL Studio 실행** 후 스크립트 로드 확인
2. **Keystation 88 MK3 연결** 확인
3. **코드 연주 테스트**:

```
🎵 C major 코드 테스트:
- C, E, G 키를 동시에 0.5초 이상 누르기
- 콘솔에 "🎼 코드 감지: C major" 메시지 확인
- 자동으로 솔로가 채널 2에서 재생되는지 확인

🎵 A minor 코드 테스트:  
- A, C, E 키를 동시에 누르기
- "🎼 코드 감지: A minor" 확인
- 다른 스타일의 솔로 패턴 재생 확인
```

### 고급 테스트
```
🎼 코드 진행 테스트:
1. C major → A minor → F major → G major 순서로 연주
2. 각 코드마다 다른 솔로 패턴이 생성되는지 확인
3. Jazz/Blues/Classical 스타일이 섞여서 나오는지 확인

🎼 7th 코드 테스트:
1. C, E, G, Bb (C7) 연주
2. "🎼 코드 감지: C dom7" 메시지 확인  
3. 더 복잡한 jazz 솔로 패턴 재생 확인
```

## 🎛️ 시스템 설정

### 솔로 채널 변경
```python
# FL Studio Script Console에서 실행
set_solo_channel(3)  # 채널 3으로 변경
```

### 스타일 선호도 조정
```python  
# Jazz 선호도를 높이기 (0.0-1.0)
update_style_preference("jazz", 0.9)

# Blues 선호도 낮추기
update_style_preference("blues", 0.5)
```

### 코드 감지 민감도 조정
```python
# 코드 감지 지연시간 설정 (초)
set_chord_detection_delay(0.5)  # 0.5초 후 코드 인식
```

## 🎵 지원되는 코드 종류

### 기본 코드
- **Major**: C, D, E, F, G, A, B (메이저)
- **Minor**: Cm, Dm, Em, Fm, Gm, Am, Bm (마이너)  
- **Power**: C5, D5, E5... (파워코드)

### 확장 코드
- **7th**: C7, Cm7, Cmaj7 (세븐스)
- **9th**: C9, Cm9, Cmaj9 (나인스)
- **6th**: C6, Cm6 (식스)
- **Sus**: Csus2, Csus4, C7sus4 (서스)

### 특수 코드
- **Diminished**: Cdim, Cdim7 (디미니시드)
- **Augmented**: Caug (어그멘티드)
- **Minor Major 7**: CmMaj7

## 🎨 솔로 스타일 특징

### Jazz Style (기본 선호도: 80%)
```
특징: 복잡한 스케일, 크로매틱 패시지, 스윙 리듬
패턴: 상행/하행 스케일, 아르페지오, 블루노트 활용
예시 코드: Cmaj7 → Am7 → Dm7 → G7
```

### Blues Style (기본 선호도: 90%)  
```
특징: 펜타토닉 스케일, 블루노트, 벤딩 효과
패턴: 블루스 스케일 위주, 반복적 모티브
예시 코드: C7 → F7 → G7 → C7
```

### Classical Style (기본 선호도: 60%)
```
특징: 아르페지오, 스케일 패시지, 우아한 멜로디
패턴: 상하행 아르페지오, 순차진행
예시 코드: C → Am → F → G
```

### Rock Style (기본 선호도: 70%)
```
특징: 파워풀한 리프, 옥타브 도약, 리듬감
패턴: 파워코드 기반, 강한 어택
예시 코드: C5 → G5 → Am5 → F5
```

## 🔧 문제 해결

### 코드가 인식되지 않는 경우
1. **MIDI 연결 확인**: FL Studio MIDI Settings에서 Keystation 활성화 확인
2. **지연시간 조정**: 코드를 0.5초 이상 길게 누르기
3. **노트 개수**: 최소 2개 이상의 노트를 동시에 누르기

### 솔로가 재생되지 않는 경우  
1. **채널 설정**: 솔로 채널에 악기가 로드되어 있는지 확인
2. **볼륨 확인**: 해당 채널의 볼륨이 켜져 있는지 확인
3. **콘솔 메시지**: FL Studio 콘솔에서 에러 메시지 확인

### 원하지 않는 스타일이 나오는 경우
```python
# 선호도 조정
update_style_preference("jazz", 1.0)    # Jazz 100%
update_style_preference("blues", 0.0)   # Blues 0%  
update_style_preference("classical", 0.5) # Classical 50%
update_style_preference("rock", 0.3)    # Rock 30%
```

## 📈 시스템 확장

### 새로운 솔로 패턴 추가
`SOLO_PATTERNS` 딕셔너리에 새로운 패턴 추가:

```python
SOLO_PATTERNS["Dm_minor"] = {
    "fusion": [50, 53, 55, 58, 60, 62, 65, 67],
    "latin": [50, 52, 55, 57, 60, 62, 64, 67]
}
```

### 새로운 코드 타입 추가
`CHORD_PATTERNS`에 새로운 코드 패턴 추가:

```python
CHORD_PATTERNS[frozenset([0, 4, 6, 10])] = "aug7"  # Augmented 7th
```

## 🎯 성능 최적화

### 시스템 요구사항
- **CPU**: Intel i5 이상 또는 동급
- **RAM**: 8GB 이상 권장  
- **MIDI 지연시간**: <10ms 권장
- **FL Studio**: 버전 20 이상

### 최적화 팁
1. **버퍼 크기**: FL Studio Audio Settings에서 128 samples 이하 설정
2. **CPU 사용량**: 불필요한 플러그인 최소화
3. **MIDI 폴링**: 코드 감지 지연시간을 0.2-0.5초로 설정

## 🎉 완성!

이제 **세계 최초의 RAG 기반 실시간 즉흥 연주 시스템**이 준비되었습니다!

키보드로 코드를 연주하면:
1. 🎼 **실시간 코드 인식**
2. 🤖 **AI가 맞춤형 솔로 생성**  
3. 🎵 **FL Studio에서 자동 재생**

**Happy Improvising!** 🎹✨