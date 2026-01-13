#!/usr/bin/env python3
"""오디오 채보 모듈: WAV → MIDI 변환 (basic-pitch AI)

개선된 피아노 추출을 위한 전처리 포함:
- 오디오 정규화
- 하이패스 필터 (저주파 노이즈 제거)
- 노이즈 제거
- basic-pitch 임계값 튜닝
"""

import os
import sys
import warnings
import tempfile

# 불필요한 경고 억제
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

import numpy as np
import scipy.signal
import scipy.signal.windows

# scipy.signal.gaussian 호환성 패치 (basic-pitch용)
if not hasattr(scipy.signal, 'gaussian'):
    scipy.signal.gaussian = scipy.signal.windows.gaussian

import librosa
import soundfile as sf

# noisereduce는 선택적 (없으면 노이즈 제거 건너뜀)
try:
    import noisereduce as nr
    HAS_NOISEREDUCE = True
except ImportError:
    HAS_NOISEREDUCE = False

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import pretty_midi


# 피아노 추출 최적화 설정
class PianoExtractionConfig:
    """피아노 추출을 위한 설정"""
    # 오디오 전처리
    SAMPLE_RATE = 22050           # basic-pitch 기본 샘플레이트
    HIGH_PASS_FREQ = 30           # 하이패스 필터 주파수 (Hz) - 피아노 최저음 A0=27.5Hz
    NORMALIZE_AUDIO = True        # 오디오 정규화 여부
    REDUCE_NOISE = True           # 노이즈 제거 여부
    NOISE_REDUCTION_STRENGTH = 0.5  # 노이즈 제거 강도 (0.0-1.0)

    # basic-pitch 임계값 (피아노에 최적화)
    ONSET_THRESHOLD = 0.5         # 노트 시작 감지 임계값 (기본: 0.5)
    FRAME_THRESHOLD = 0.3         # 프레임 감지 임계값 (기본: 0.3)
    MINIMUM_NOTE_LENGTH = 58      # 최소 노트 길이 (ms) - 기본값 유지

    # 피아노 주파수 범위 (A0 ~ C8)
    PIANO_MIN_FREQ = 27.5         # A0
    PIANO_MAX_FREQ = 4186.0       # C8


def preprocess_audio(audio_path, config=None):
    """피아노 추출을 위한 오디오 전처리

    Args:
        audio_path: 입력 오디오 파일 경로
        config: PianoExtractionConfig 인스턴스 (기본: None)

    Returns:
        tuple: (전처리된 오디오 배열, 샘플레이트)
    """
    if config is None:
        config = PianoExtractionConfig()

    print("  [전처리] 오디오 로딩 중...")
    y, sr = librosa.load(audio_path, sr=config.SAMPLE_RATE)

    # 1. 하이패스 필터 적용 (저주파 노이즈 제거)
    print(f"  [전처리] 하이패스 필터 적용 ({config.HIGH_PASS_FREQ}Hz)...")
    nyquist = sr / 2
    high_pass_normalized = config.HIGH_PASS_FREQ / nyquist

    # Butterworth 하이패스 필터 (2차)
    b, a = scipy.signal.butter(2, high_pass_normalized, btype='high')
    y = scipy.signal.filtfilt(b, a, y)

    # 2. 노이즈 제거 (noisereduce 사용)
    if config.REDUCE_NOISE and HAS_NOISEREDUCE:
        print("  [전처리] 노이즈 제거 중...")
        y = nr.reduce_noise(
            y=y,
            sr=sr,
            prop_decrease=config.NOISE_REDUCTION_STRENGTH,
            stationary=False  # 비정상적 노이즈에도 대응
        )
    elif config.REDUCE_NOISE and not HAS_NOISEREDUCE:
        print("  [전처리] noisereduce 미설치, 노이즈 제거 건너뜀")

    # 3. 오디오 정규화
    if config.NORMALIZE_AUDIO:
        print("  [전처리] 오디오 정규화 중...")
        y = librosa.util.normalize(y)

    return y, sr


def transcribe_audio_to_midi(audio_path, output_dir='output', config=None):
    """오디오 파일을 MIDI로 변환 (피아노 추출 최적화)

    Args:
        audio_path: 입력 오디오 파일 경로 (WAV)
        output_dir: 출력 디렉토리 (기본: output/)
        config: PianoExtractionConfig 인스턴스 (기본: None)

    Returns:
        str: 생성된 MIDI 파일 경로
    """
    if config is None:
        config = PianoExtractionConfig()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"{audio_path} → MIDI 변환 중...")

    # 1. 오디오 전처리
    y_processed, sr = preprocess_audio(audio_path, config)

    # 전처리된 오디오를 임시 파일로 저장
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        tmp_path = tmp_file.name
        sf.write(tmp_path, y_processed, sr)

    try:
        # 2. basic-pitch 추론 (튜닝된 파라미터)
        print("  [채보] basic-pitch AI 추론 중...")
        print(f"    - onset_threshold: {config.ONSET_THRESHOLD}")
        print(f"    - frame_threshold: {config.FRAME_THRESHOLD}")
        print(f"    - minimum_note_length: {config.MINIMUM_NOTE_LENGTH}ms")

        model_output, midi_data, note_events = predict(
            tmp_path,
            model_or_model_path=ICASSP_2022_MODEL_PATH,
            onset_threshold=config.ONSET_THRESHOLD,
            frame_threshold=config.FRAME_THRESHOLD,
            minimum_note_length=config.MINIMUM_NOTE_LENGTH,
        )

        # 3. MIDI 파일 저장
        base_name = os.path.basename(audio_path).rsplit('.', 1)[0]
        midi_path = os.path.join(output_dir, f"{base_name}_basic_pitch.mid")
        midi_data.write(midi_path)

        print(f"  [채보] 감지된 노트 수: {len(note_events)}")

    finally:
        # 임시 파일 정리
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return midi_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python transcriber.py <audio_file>")
    else:
        path = sys.argv[1]
        midi_file = transcribe_audio_to_midi(path)
        print(f"MIDI 생성 완료: {midi_file}")
