#!/usr/bin/env python3
"""오디오 채보 모듈: WAV → MIDI 변환 (basic-pitch AI)"""

import os
import sys
import warnings

# 불필요한 경고 억제
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

import scipy.signal
import scipy.signal.windows

# scipy.signal.gaussian 호환성 패치 (basic-pitch용)
if not hasattr(scipy.signal, 'gaussian'):
    scipy.signal.gaussian = scipy.signal.windows.gaussian

from basic_pitch.inference import predict_and_save


def transcribe_audio_to_midi(audio_path, output_dir='output'):
    """오디오 파일을 MIDI로 변환

    Args:
        audio_path: 입력 오디오 파일 경로 (WAV)
        output_dir: 출력 디렉토리 (기본: output/)

    Returns:
        str: 생성된 MIDI 파일 경로
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"{audio_path} → MIDI 변환 중...")

    # ONNX 모델 경로 동적 탐색
    try:
        import basic_pitch
        bp_path = os.path.dirname(basic_pitch.__file__)
        onnx_model_path = os.path.join(bp_path, 'saved_models', 'icassp_2022', 'nmp.onnx')
    except Exception:
        onnx_model_path = None

    # basic-pitch 추론
    predict_and_save(
        audio_path_list=[audio_path],
        output_directory=output_dir,
        save_midi=True,
        sonify_midi=False,
        save_model_outputs=False,
        save_notes=False,
        model_or_model_path=onnx_model_path,
    )

    # basic-pitch는 파일명에 "_basic_pitch.mid"를 붙임
    base_name = os.path.basename(audio_path).rsplit('.', 1)[0]
    midi_path = os.path.join(output_dir, f"{base_name}_basic_pitch.mid")
    return midi_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python transcriber.py <audio_file>")
    else:
        path = sys.argv[1]
        midi_file = transcribe_audio_to_midi(path)
        print(f"MIDI 생성 완료: {midi_file}")
