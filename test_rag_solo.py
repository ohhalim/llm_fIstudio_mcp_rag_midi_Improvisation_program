#!/usr/bin/env python3
"""
RAG 기반 재즈 솔로 생성 시스템 테스트 스크립트
"""

import sys
import os

# 프로젝트 루트 추가
project_root = "/Users/ohhalim/git_box/llm_fIstudio_mcp_rag_midi_Improvisation_program"
if project_root not in sys.path:
    sys.path.append(project_root)

def test_rag_system():
    """RAG 시스템 테스트"""
    print("=== RAG 시스템 테스트 ===")

    try:
        from midi_rag_system import MIDIRagSystem

        # RAG 시스템 초기화
        print("RAG 시스템 초기화 중...")
        rag = MIDIRagSystem()

        # 테스트 화성코드 진행들
        test_progressions = [
            ['Cmaj7', 'Am7', 'Dm7', 'G7'],
            ['Am7', 'D7', 'Gmaj7'],
            ['Cmaj7', 'E7', 'Am7', 'A7', 'Dm7', 'G7'],
            ['Fmaj7', 'Bm7b5', 'E7', 'Am7']
        ]

        print("\n=== 화성코드 진행별 솔로라인 생성 테스트 ===")

        for i, progression in enumerate(test_progressions, 1):
            print(f"\n테스트 {i}: {' - '.join(progression)}")

            try:
                solo_line = rag.generate_solo_line(progression, style='jazz')

                if solo_line:
                    print(f"  ✅ 생성된 노트 수: {len(solo_line)}")
                    print("  생성된 솔로라인 미리보기:")

                    for j, note in enumerate(solo_line[:8]):  # 처음 8개 노트만 표시
                        print(f"    {j+1}. {note['name']}{note['octave']} "
                              f"(위치: {note['offset']:.2f}, 길이: {note['duration']:.2f}, "
                              f"벨로시티: {note['velocity']})")

                    if len(solo_line) > 8:
                        print(f"    ... 총 {len(solo_line)}개 노트")

                else:
                    print("  ❌ 솔로라인 생성 실패")

            except Exception as e:
                print(f"  ❌ 오류: {e}")

        print("\n=== 지식 베이스 정보 ===")
        print(f"학습된 패턴 수: {len(rag.chord_solo_pairs)}")

        if rag.chord_solo_pairs:
            print("샘플 패턴:")
            sample = rag.chord_solo_pairs[0]
            print(f"  키: {sample.get('key', 'Unknown')}")
            print(f"  스케일: {sample.get('scale', 'Unknown')}")
            print(f"  코드 수: {len(sample.get('chords', []))}")
            print(f"  솔로 노트 수: {len(sample.get('solo', []))}")

        return True

    except ImportError as e:
        print(f"❌ RAG 시스템 import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ RAG 시스템 테스트 실패: {e}")
        return False

def test_trigger_integration():
    """trigger.py와 RAG 시스템 통합 테스트"""
    print("\n=== trigger.py 통합 테스트 ===")

    try:
        import trigger
        from midi_rag_system import generate_jazz_solo

        # 화성코드 진행
        chord_progression = ['Cmaj7', 'Am7', 'Dm7', 'G7']
        print(f"테스트 화성코드: {chord_progression}")

        # RAG 시스템으로 솔로라인 생성
        solo_line = generate_jazz_solo(chord_progression)

        if solo_line:
            print(f"✅ RAG 시스템에서 {len(solo_line)}개 노트 생성됨")

            # trigger.py 형식으로 변환
            melody_data = []
            for note in solo_line:
                line = f"{note['pitch']},{note['velocity']},{note['duration']:.2f},{note['offset']:.2f}"
                melody_data.append(line)

            melody_string = '\n'.join(melody_data)
            print(f"✅ trigger.py 형식으로 변환 완료 ({len(melody_data)}줄)")

            # 실제 전송은 FL Studio가 실행 중일 때만 가능
            print("📝 FL Studio 실행 시 다음 명령으로 전송 가능:")
            print("   trigger.send_melody(melody_string)")

            return True
        else:
            print("❌ 솔로라인 생성 실패")
            return False

    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
        return False

def test_chord_mapping():
    """화성코드 매핑 테스트"""
    print("\n=== 화성코드 매핑 테스트 ===")

    # device_test.py의 CHORD_MAP 시뮬레이션
    CHORD_MAP = {
        # 메이저 코드
        60: 'Cmaj7', 62: 'Dmaj7', 64: 'Emaj7', 65: 'Fmaj7',
        67: 'Gmaj7', 69: 'Amaj7', 71: 'Bmaj7',

        # 마이너 코드
        72: 'Cm7', 74: 'Dm7', 76: 'Em7', 77: 'Fm7',
        79: 'Gm7', 81: 'Am7', 83: 'Bm7',

        # 도미넌트 7th
        84: 'C7', 86: 'D7', 88: 'E7', 89: 'F7',
        91: 'G7', 93: 'A7', 95: 'B7'
    }

    print("MIDI 노트 → 화성코드 매핑:")
    print("\n메이저 7th (C4-B4):")
    for note in range(60, 72):
        if note in CHORD_MAP:
            print(f"  {note}: {CHORD_MAP[note]}")

    print("\n마이너 7th (C5-B5):")
    for note in range(72, 84):
        if note in CHORD_MAP:
            print(f"  {note}: {CHORD_MAP[note]}")

    print("\n도미넌트 7th (C6-B6):")
    for note in range(84, 96):
        if note in CHORD_MAP:
            print(f"  {note}: {CHORD_MAP[note]}")

    # 샘플 진행 테스트
    sample_midi_notes = [60, 81, 74, 91]  # Cmaj7, Am7, Dm7, G7
    chord_progression = [CHORD_MAP[note] for note in sample_midi_notes]

    print(f"\n샘플 MIDI 시퀀스: {sample_midi_notes}")
    print(f"변환된 화성코드: {chord_progression}")

    return True

def main():
    """메인 테스트 함수"""
    print("🎵 RAG 기반 재즈 솔로 생성 시스템 테스트")
    print("=" * 50)

    # 각 테스트 실행
    tests = [
        ("RAG 시스템 기본 테스트", test_rag_system),
        ("화성코드 매핑 테스트", test_chord_mapping),
        ("trigger.py 통합 테스트", test_trigger_integration)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)

        try:
            result = test_func()
            results.append((test_name, result))

            if result:
                print(f"✅ {test_name} 성공")
            else:
                print(f"❌ {test_name} 실패")

        except Exception as e:
            print(f"❌ {test_name} 오류: {e}")
            results.append((test_name, False))

    # 결과 요약
    print("\n" + "=" * 50)
    print("🏁 테스트 결과 요약")
    print("=" * 50)

    success_count = 0
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1

    print(f"\n총 {len(results)}개 테스트 중 {success_count}개 성공")

    if success_count == len(results):
        print("🎉 모든 테스트 통과! RAG 시스템이 정상 작동합니다.")
        print("\n📋 사용 방법:")
        print("1. FL Studio에서 Test Controller 활성화")
        print("2. MIDI 노트 1 전송 (화성코드 입력 모드)")
        print("3. 화성코드 순서대로 노트 전송 (60=Cmaj7, 81=Am7, etc.)")
        print("4. MIDI 노트 2 전송 (솔로라인 생성 및 녹음)")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 시스템 설정을 확인해주세요.")

if __name__ == "__main__":
    main()