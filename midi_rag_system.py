# midi_rag_system.py
# MIDI RAG (Retrieval-Augmented Generation) System for Jazz Solo Generation

import os
import json
import numpy as np
import music21 as m21
from music21 import stream, note, chord, interval, scale, key
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pretty_midi
import pickle
from typing import List, Dict, Tuple, Optional
import random

class MIDIRagSystem:
    def __init__(self, midi_directory: str = "midi_data"):
        """
        MIDI RAG 시스템 초기화

        Args:
            midi_directory: MIDI 파일들이 저장된 디렉토리
        """
        self.midi_directory = midi_directory
        self.chord_progressions = []
        self.solo_patterns = []
        self.chord_solo_pairs = []
        self.vectorizer = TfidfVectorizer()
        self.chord_vectors = None
        self.pattern_clusters = None

        # 음악 이론 데이터베이스
        self.scale_patterns = {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'dorian': [0, 2, 3, 5, 7, 9, 10],
            'mixolydian': [0, 2, 4, 5, 7, 9, 10],
            'minor': [0, 2, 3, 5, 7, 8, 10],
            'blues': [0, 3, 5, 6, 7, 10],
            'pentatonic_major': [0, 2, 4, 7, 9],
            'pentatonic_minor': [0, 3, 5, 7, 10],
            'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        }

        self.chord_scale_map = {
            'maj': 'major',
            'min': 'dorian',
            '7': 'mixolydian',
            'm7': 'dorian',
            'maj7': 'major',
            'min7': 'dorian',
            'dom7': 'mixolydian',
            'dim': 'minor',
            'aug': 'chromatic'
        }

        # 초기화
        self.ensure_midi_directory()
        self.load_or_create_knowledge_base()

    def ensure_midi_directory(self):
        """MIDI 디렉토리가 없으면 생성"""
        if not os.path.exists(self.midi_directory):
            os.makedirs(self.midi_directory)
            print(f"Created MIDI directory: {self.midi_directory}")

    def analyze_midi_file(self, file_path: str) -> Dict:
        """
        MIDI 파일을 분석하여 화성코드와 솔로라인 추출

        Args:
            file_path: MIDI 파일 경로

        Returns:
            분석된 데이터 딕셔너리
        """
        try:
            # music21로 MIDI 파일 로드
            score = m21.converter.parse(file_path)

            # 키 추출
            key_sig = score.analyze('key')

            # 화성코드 추출 (낮은 음역대)
            chord_track = self.extract_chords(score)

            # 솔로라인 추출 (높은 음역대)
            solo_track = self.extract_solo_line(score)

            # 리듬 패턴 분석
            rhythm_pattern = self.analyze_rhythm(solo_track)

            # 음계 패턴 분석
            scale_pattern = self.analyze_scale_usage(solo_track, key_sig)

            return {
                'file_path': file_path,
                'key': str(key_sig),
                'chord_progression': chord_track,
                'solo_line': solo_track,
                'rhythm_pattern': rhythm_pattern,
                'scale_pattern': scale_pattern,
                'tempo': self.extract_tempo(score)
            }

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def extract_chords(self, score) -> List[Dict]:
        """화성코드 추출"""
        chords = []

        # 모든 파트에서 화성코드 찾기
        for part in score.parts:
            for element in part.flat.notesAndRests:
                if isinstance(element, m21.chord.Chord):
                    chord_symbol = self.chord_to_symbol(element)
                    chords.append({
                        'symbol': chord_symbol,
                        'root': element.root().name,
                        'quality': self.get_chord_quality(element),
                        'offset': float(element.offset),
                        'duration': float(element.duration.quarterLength)
                    })

        return chords

    def extract_solo_line(self, score) -> List[Dict]:
        """솔로라인 추출"""
        solo_notes = []

        # 가장 높은 음역대의 멜로디 추출
        highest_part = None
        highest_avg_pitch = 0

        for part in score.parts:
            notes_in_part = [n for n in part.flat.notes if isinstance(n, m21.note.Note)]
            if notes_in_part:
                avg_pitch = sum(n.pitch.midi for n in notes_in_part) / len(notes_in_part)
                if avg_pitch > highest_avg_pitch:
                    highest_avg_pitch = avg_pitch
                    highest_part = part

        if highest_part:
            for element in highest_part.flat.notesAndRests:
                if isinstance(element, m21.note.Note):
                    solo_notes.append({
                        'pitch': element.pitch.midi,
                        'name': element.pitch.name,
                        'octave': element.pitch.octave,
                        'offset': float(element.offset),
                        'duration': float(element.duration.quarterLength),
                        'velocity': getattr(element, 'velocity', 80)
                    })

        return solo_notes

    def analyze_rhythm(self, solo_notes: List[Dict]) -> Dict:
        """리듬 패턴 분석"""
        if not solo_notes:
            return {'pattern': 'empty'}

        durations = [note['duration'] for note in solo_notes]

        # 주요 리듬 단위 분석
        rhythm_units = {}
        for duration in durations:
            key = f"{duration:.2f}"
            rhythm_units[key] = rhythm_units.get(key, 0) + 1

        # 가장 많이 사용된 리듬 단위
        primary_rhythm = max(rhythm_units.items(), key=lambda x: x[1])[0]

        return {
            'primary_rhythm': float(primary_rhythm),
            'rhythm_variety': len(rhythm_units),
            'pattern': 'varied' if len(rhythm_units) > 3 else 'simple'
        }

    def analyze_scale_usage(self, solo_notes: List[Dict], key_sig) -> Dict:
        """음계 사용 패턴 분석"""
        if not solo_notes:
            return {'scale': 'unknown'}

        # 사용된 음정들을 키에 상대적인 계급으로 변환
        key_tonic = key_sig.tonic.pitchClass
        scale_degrees = []

        for note_data in solo_notes:
            pitch_class = note_data['pitch'] % 12
            degree = (pitch_class - key_tonic) % 12
            scale_degrees.append(degree)

        # 각 스케일과의 일치도 계산
        scale_matches = {}
        for scale_name, scale_pattern in self.scale_patterns.items():
            matches = sum(1 for degree in set(scale_degrees) if degree in scale_pattern)
            scale_matches[scale_name] = matches / len(set(scale_degrees)) if scale_degrees else 0

        best_scale = max(scale_matches.items(), key=lambda x: x[1])[0]

        return {
            'best_scale': best_scale,
            'scale_coverage': scale_matches[best_scale],
            'used_degrees': list(set(scale_degrees))
        }

    def extract_tempo(self, score) -> int:
        """템포 추출"""
        tempo_marks = score.flat.metronomeMarks
        if tempo_marks:
            return int(tempo_marks[0].number)
        return 120  # 기본값

    def chord_to_symbol(self, chord_obj) -> str:
        """화성코드를 심볼로 변환"""
        try:
            return chord_obj.figure
        except:
            return f"{chord_obj.root().name}{self.get_chord_quality(chord_obj)}"

    def get_chord_quality(self, chord_obj) -> str:
        """화성코드 품질 분석"""
        intervals = [interval.Interval(chord_obj.root(), p).semitones for p in chord_obj.pitches[1:]]

        if 4 in intervals and 7 in intervals:
            return 'maj'
        elif 3 in intervals and 7 in intervals:
            return 'min'
        elif 4 in intervals and 7 in intervals and 10 in intervals:
            return '7'
        elif 3 in intervals and 7 in intervals and 10 in intervals:
            return 'm7'
        else:
            return 'unknown'

    def learn_from_midi_files(self):
        """MIDI 파일들로부터 학습"""
        print("Learning from MIDI files...")

        midi_files = [f for f in os.listdir(self.midi_directory) if f.endswith(('.mid', '.midi'))]

        if not midi_files:
            print("No MIDI files found. Creating sample knowledge base...")
            self.create_sample_knowledge_base()
            return

        for file_name in midi_files:
            file_path = os.path.join(self.midi_directory, file_name)
            print(f"Analyzing: {file_name}")

            analysis = self.analyze_midi_file(file_path)
            if analysis:
                self.chord_progressions.append(analysis['chord_progression'])
                self.solo_patterns.append(analysis['solo_line'])
                self.chord_solo_pairs.append({
                    'chords': analysis['chord_progression'],
                    'solo': analysis['solo_line'],
                    'key': analysis['key'],
                    'scale': analysis['scale_pattern']['best_scale'],
                    'rhythm': analysis['rhythm_pattern']
                })

        self.build_vectors()
        print(f"Learned from {len(self.chord_solo_pairs)} MIDI files")

    def create_sample_knowledge_base(self):
        """샘플 지식 베이스 생성"""
        sample_patterns = [
            {
                'chords': [
                    {'symbol': 'Cmaj7', 'root': 'C', 'quality': 'maj7'},
                    {'symbol': 'Am7', 'root': 'A', 'quality': 'm7'},
                    {'symbol': 'Dm7', 'root': 'D', 'quality': 'm7'},
                    {'symbol': 'G7', 'root': 'G', 'quality': '7'}
                ],
                'solo': self.generate_sample_solo_line([60, 69, 62, 67], 'major'),
                'key': 'C major',
                'scale': 'major',
                'rhythm': {'primary_rhythm': 0.5, 'pattern': 'simple'}
            },
            {
                'chords': [
                    {'symbol': 'Dm7', 'root': 'D', 'quality': 'm7'},
                    {'symbol': 'G7', 'root': 'G', 'quality': '7'},
                    {'symbol': 'Cmaj7', 'root': 'C', 'quality': 'maj7'}
                ],
                'solo': self.generate_sample_solo_line([62, 67, 60], 'dorian'),
                'key': 'C major',
                'scale': 'dorian',
                'rhythm': {'primary_rhythm': 0.25, 'pattern': 'varied'}
            }
        ]

        self.chord_solo_pairs = sample_patterns
        self.build_vectors()
        print("Created sample knowledge base")

    def generate_sample_solo_line(self, chord_roots: List[int], scale_type: str) -> List[Dict]:
        """샘플 솔로라인 생성"""
        solo_line = []
        scale_pattern = self.scale_patterns.get(scale_type, self.scale_patterns['major'])

        for i, root in enumerate(chord_roots):
            base_pitch = root + 12  # 한 옥타브 위

            # 각 코드에 대해 2-4개의 노트 생성
            for j in range(random.randint(2, 4)):
                scale_degree = random.choice(scale_pattern)
                pitch = base_pitch + scale_degree

                solo_line.append({
                    'pitch': pitch,
                    'name': m21.pitch.Pitch(pitch).name,
                    'octave': pitch // 12 - 1,
                    'offset': i * 2 + j * 0.5,
                    'duration': random.choice([0.25, 0.5, 1.0]),
                    'velocity': random.randint(80, 120)
                })

        return solo_line

    def build_vectors(self):
        """벡터화 및 클러스터링"""
        if not self.chord_solo_pairs:
            print("No chord-solo pairs available for vectorization")
            return

        try:
            # 화성코드 진행을 텍스트로 변환
            chord_texts = []
            for pair in self.chord_solo_pairs:
                if 'chords' in pair and pair['chords']:
                    chord_text = ' '.join([f"{c.get('root', 'C')}{c.get('quality', 'maj')}" for c in pair['chords']])
                    chord_texts.append(chord_text)

            # TF-IDF 벡터화
            if chord_texts:
                self.chord_vectors = self.vectorizer.fit_transform(chord_texts)
                print(f"Built chord vectors for {len(chord_texts)} progressions")

                # 솔로 패턴 클러스터링
                solo_features = []
                for pair in self.chord_solo_pairs:
                    if 'solo' in pair:
                        features = self.extract_solo_features(pair['solo'])
                        solo_features.append(features)

                if solo_features and len(solo_features) > 1:
                    n_clusters = min(5, len(solo_features))
                    self.pattern_clusters = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    self.pattern_clusters.fit(solo_features)
                    print(f"Built {n_clusters} clusters for solo patterns")

        except Exception as e:
            print(f"Error in build_vectors: {e}")
            self.chord_vectors = None
            self.pattern_clusters = None

    def extract_solo_features(self, solo_line: List[Dict]) -> List[float]:
        """솔로라인에서 특징 추출"""
        if not solo_line:
            return [0] * 10

        pitches = [note['pitch'] for note in solo_line]
        durations = [note['duration'] for note in solo_line]

        features = [
            np.mean(pitches),  # 평균 음높이
            np.std(pitches),   # 음높이 편차
            max(pitches) - min(pitches),  # 음역대
            np.mean(durations),  # 평균 지속시간
            np.std(durations),   # 지속시간 편차
            len(solo_line),      # 노트 개수
            len(set(pitches)),   # 고유 음높이 개수
            sum(1 for i in range(1, len(pitches)) if pitches[i] > pitches[i-1]),  # 상행 움직임
            sum(1 for i in range(1, len(pitches)) if pitches[i] < pitches[i-1]),  # 하행 움직임
            sum(1 for i in range(1, len(pitches)) if abs(pitches[i] - pitches[i-1]) > 7)  # 큰 점프
        ]

        return features

    def find_similar_progressions(self, input_chords: List[str], top_k: int = 3) -> List[Dict]:
        """입력 화성코드와 유사한 진행 찾기"""
        if self.chord_vectors is None or len(self.chord_solo_pairs) == 0:
            return []

        try:
            # 입력을 벡터로 변환
            input_text = ' '.join(input_chords)
            input_vector = self.vectorizer.transform([input_text])

            # 코사인 유사도 계산
            similarities = cosine_similarity(input_vector, self.chord_vectors)[0]

            # 상위 k개 선택
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            results = []
            for idx in top_indices:
                results.append({
                    'similarity': similarities[idx],
                    'pattern': self.chord_solo_pairs[idx],
                    'index': idx
                })

            return results

        except Exception as e:
            print(f"Error in finding similar progressions: {e}")
            return []

    def generate_solo_line(self, input_chords: List[str], style: str = 'jazz') -> List[Dict]:
        """화성코드에 맞는 솔로라인 생성"""
        print(f"Generating solo line for chords: {input_chords}")

        # 유사한 패턴 찾기
        similar_patterns = self.find_similar_progressions(input_chords)

        if not similar_patterns:
            print("No similar patterns found, generating basic solo line")
            return self.generate_basic_solo_line(input_chords)

        print(f"Found {len(similar_patterns)} similar patterns")

        # 가장 유사한 패턴을 기반으로 솔로라인 생성
        best_pattern = similar_patterns[0]['pattern']

        # 기본 솔로라인 구조를 가져와서 수정
        generated_solo = []
        chord_duration = 2.0  # 각 코드당 2비트

        for i, chord_symbol in enumerate(input_chords):
            chord_root = self.extract_root_from_symbol(chord_symbol)
            chord_quality = self.extract_quality_from_symbol(chord_symbol)

            # 해당 코드에 맞는 스케일 선택
            scale_type = self.chord_scale_map.get(chord_quality, 'major')
            scale_pattern = self.scale_patterns[scale_type]

            # 베이스 패턴에서 영감을 받아 노트 생성
            base_pattern = best_pattern['solo']
            pattern_length = len(base_pattern)

            # 각 코드에 대해 노트 생성
            notes_per_chord = random.randint(3, 6)
            for j in range(notes_per_chord):
                # 패턴에서 상대적 위치의 노트 참조
                pattern_idx = (j * pattern_length // notes_per_chord) % pattern_length
                reference_note = base_pattern[pattern_idx] if base_pattern else None

                # 새로운 노트 생성
                scale_degree = random.choice(scale_pattern)
                base_pitch = chord_root + 24  # 2옥타브 위
                pitch = base_pitch + scale_degree

                # 옥타브 조정 (너무 높거나 낮지 않게)
                while pitch > 84:  # C6
                    pitch -= 12
                while pitch < 60:  # C4
                    pitch += 12

                # 리듬 패턴 적용
                rhythm = best_pattern['rhythm']['primary_rhythm']
                duration = random.choice([rhythm, rhythm * 2, rhythm * 0.5])

                # 벨로시티 변화
                base_velocity = 100
                if reference_note:
                    base_velocity = reference_note.get('velocity', 100)
                velocity = base_velocity + random.randint(-20, 20)
                velocity = max(60, min(127, velocity))

                generated_solo.append({
                    'pitch': pitch,
                    'name': m21.pitch.Pitch(pitch).name,
                    'octave': pitch // 12 - 1,
                    'offset': i * chord_duration + j * (chord_duration / notes_per_chord),
                    'duration': duration,
                    'velocity': velocity
                })

        return generated_solo

    def generate_basic_solo_line(self, input_chords: List[str]) -> List[Dict]:
        """기본 솔로라인 생성 (패턴이 없을 때)"""
        generated_solo = []
        chord_duration = 2.0

        for i, chord_symbol in enumerate(input_chords):
            chord_root = self.extract_root_from_symbol(chord_symbol)
            chord_quality = self.extract_quality_from_symbol(chord_symbol)

            scale_type = self.chord_scale_map.get(chord_quality, 'major')
            scale_pattern = self.scale_patterns[scale_type]

            # 간단한 아르페지오 패턴
            notes_per_chord = 4
            for j in range(notes_per_chord):
                scale_degree = scale_pattern[j % len(scale_pattern)]
                pitch = chord_root + 24 + scale_degree

                generated_solo.append({
                    'pitch': pitch,
                    'name': m21.pitch.Pitch(pitch).name,
                    'octave': pitch // 12 - 1,
                    'offset': i * chord_duration + j * (chord_duration / notes_per_chord),
                    'duration': 0.5,
                    'velocity': 100
                })

        return generated_solo

    def extract_root_from_symbol(self, chord_symbol: str) -> int:
        """코드 심볼에서 근음 추출"""
        note_map = {'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71}

        root_name = chord_symbol[0].upper()
        root_pitch = note_map.get(root_name, 60)

        # 샤프/플랫 처리
        if len(chord_symbol) > 1:
            if chord_symbol[1] == '#':
                root_pitch += 1
            elif chord_symbol[1] == 'b':
                root_pitch -= 1

        return root_pitch

    def extract_quality_from_symbol(self, chord_symbol: str) -> str:
        """코드 심볼에서 품질 추출"""
        symbol_lower = chord_symbol.lower()

        if 'maj7' in symbol_lower:
            return 'maj7'
        elif 'm7' in symbol_lower or 'min7' in symbol_lower:
            return 'm7'
        elif '7' in symbol_lower:
            return '7'
        elif 'min' in symbol_lower or 'm' in symbol_lower:
            return 'min'
        elif 'maj' in symbol_lower:
            return 'maj'
        else:
            return 'maj'  # 기본값

    def save_knowledge_base(self, file_path: str = "midi_knowledge_base.pkl"):
        """지식 베이스 저장"""
        data = {
            'chord_solo_pairs': self.chord_solo_pairs,
            'vectorizer': self.vectorizer,
            'pattern_clusters': self.pattern_clusters
        }

        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Knowledge base saved to {file_path}")

    def load_knowledge_base(self, file_path: str = "midi_knowledge_base.pkl") -> bool:
        """지식 베이스 로드"""
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)

            self.chord_solo_pairs = data['chord_solo_pairs']
            self.vectorizer = data['vectorizer']
            self.pattern_clusters = data['pattern_clusters']

            if self.chord_solo_pairs:
                self.build_vectors()

            print(f"Knowledge base loaded from {file_path}")
            return True
        except FileNotFoundError:
            print(f"Knowledge base file not found: {file_path}")
            return False
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return False

    def load_or_create_knowledge_base(self):
        """지식 베이스 로드 또는 생성"""
        if not self.load_knowledge_base():
            print("Creating new knowledge base...")
            self.learn_from_midi_files()
            self.save_knowledge_base()

# 전역 RAG 시스템 인스턴스
midi_rag = None

def initialize_rag_system():
    """RAG 시스템 초기화"""
    global midi_rag
    if midi_rag is None:
        midi_rag = MIDIRagSystem()
    return midi_rag

def generate_jazz_solo(chord_progression: List[str]) -> List[Dict]:
    """화성코드 진행에 맞는 재즈 솔로 생성"""
    rag_system = initialize_rag_system()
    return rag_system.generate_solo_line(chord_progression, style='jazz')

if __name__ == "__main__":
    # 테스트
    rag_system = MIDIRagSystem()

    # 샘플 화성코드 진행
    test_chords = ['Cmaj7', 'Am7', 'Dm7', 'G7']

    # 솔로라인 생성
    solo_line = rag_system.generate_solo_line(test_chords)

    print("Generated solo line:")
    for note in solo_line:
        print(f"  {note['name']}{note['octave']} at {note['offset']:.2f} beats, duration {note['duration']:.2f}")