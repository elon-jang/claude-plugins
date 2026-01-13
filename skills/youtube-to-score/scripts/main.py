#!/usr/bin/env python3
"""YouTube-to-Score: YouTube 피아노 영상을 악보로 변환"""

import os
import sys
import warnings
import logging

# 불필요한 경고 억제
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
logging.getLogger('root').setLevel(logging.ERROR)

from downloader import download_audio, DownloadError
from transcriber import transcribe_audio_to_midi
from renderer import midi_to_score


def run_pipeline(youtube_url, output_dir='output', download_dir='downloads'):
    """YouTube URL에서 악보 생성 파이프라인 실행

    Args:
        youtube_url: YouTube 영상 URL
        output_dir: 출력 디렉토리 (기본: output/)
        download_dir: 다운로드 디렉토리 (기본: downloads/)

    Returns:
        dict: 생성된 파일 경로들 (midi, xml, pdf)
    """
    results = {}

    print("=== 1단계: 오디오 다운로드 ===")
    try:
        audio_file, is_trimmed = download_audio(youtube_url, download_dir)
    except DownloadError as e:
        print(f"오류: {e}")
        sys.exit(1)

    print(f"오디오 다운로드 완료: {audio_file}")
    if is_trimmed:
        print("(첫 10분만 추출됨)")

    print("\n=== 2단계: MIDI 변환 ===")
    midi_file = transcribe_audio_to_midi(audio_file, output_dir)
    print(f"MIDI 생성 완료: {midi_file}")
    results['midi'] = midi_file

    print("\n=== 3단계: 악보 렌더링 ===")
    output_pdf = midi_file.replace('.mid', '.pdf')
    xml_file, pdf_file = midi_to_score(midi_file, output_pdf)
    results['xml'] = xml_file
    results['pdf'] = pdf_file

    print("\n=== 변환 완료 ===")
    print(f"MIDI: {midi_file}")
    print(f"MusicXML: {xml_file}")
    if pdf_file:
        print(f"PDF: {pdf_file}")

    return results


def main():
    """CLI 진입점"""
    if len(sys.argv) < 2:
        print("YouTube-to-Score: YouTube 피아노 영상을 악보로 변환")
        print()
        print("사용법:")
        print("  python main.py <youtube_url>")
        print()
        print("예시:")
        print("  python main.py \"https://youtube.com/watch?v=...\"")
        print()
        print("출력:")
        print("  downloads/  - WAV 오디오 파일")
        print("  output/     - MIDI, MusicXML, PDF 파일")
        sys.exit(1)

    url = sys.argv[1]
    run_pipeline(url)


if __name__ == "__main__":
    main()
