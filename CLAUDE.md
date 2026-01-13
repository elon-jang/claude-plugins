# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube-to-Score는 YouTube 피아노 연주 영상의 오디오를 분석하여 악보(MIDI, MusicXML, PDF)를 자동 생성하는 CLI 도구입니다. 악보 제작자가 빠르게 초안 악보를 얻어 MuseScore 등에서 편집할 수 있도록 설계되었습니다.

## Commands

### Setup
```bash
# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# Python 패키지 설치
pip install yt-dlp basic-pitch music21 onnxruntime "scipy<1.15"

# 시스템 의존성 설치 (macOS)
brew install ffmpeg lilypond
```

### Run
```bash
# 전체 파이프라인: YouTube URL → 악보
python main.py "YOUTUBE_URL"

# 개별 모듈 실행:
python downloader.py "YOUTUBE_URL"       # downloads/에 WAV 저장
python transcriber.py audio.wav          # output/에 MIDI 저장
python renderer.py input.mid output.pdf  # MIDI → MusicXML + PDF
```

## Architecture

선형 3단계 파이프라인:

1. **Downloader** (`downloader.py`): `yt-dlp`로 YouTube에서 고품질 WAV 추출. 10분 초과 영상은 첫 10분만 추출. `DownloadError` 예외로 한글 오류 메시지 제공.

2. **Transcriber** (`transcriber.py`): Spotify `basic-pitch` AI 모델(ONNX 백엔드)로 오디오 → MIDI 변환. `scipy.signal.gaussian` 호환성 패치 포함.

3. **Renderer** (`renderer.py`): `music21`로 MIDI → MusicXML 변환. PDF는 기본 렌더러 시도 후 LilyPond 폴백. LilyPond 미설치 시 경고만 표시.

## Key Implementation Details

- **10분 길이 제한**: `download_audio()`는 `(filepath, is_trimmed)` 튜플 반환. 10분 초과 시 `download_ranges` 옵션으로 첫 10분만 추출
- **한글 오류 메시지**: `_get_korean_error_message()`로 yt-dlp 오류를 사용자 친화적 한글로 변환
- **ONNX 모델 경로**: transcriber가 `basic_pitch` 패키지에서 동적으로 탐색
- **PDF 렌더링**: 임시 디렉토리에서 안전한 파일명("score")으로 LilyPond 실행
- **SciPy 버전**: < 1.15 필수 (deprecated `gaussian` 함수 사용)

## Constraints

- **피아노 전용**: 다른 악기 미지원
- **macOS 전용**: 다른 OS 미지원
- **YouTube URL만**: 로컬 파일 미지원
- **단일 URL만**: 배치 처리 미지원

## Output Directories

- `downloads/`: 다운로드된 WAV 파일 (삭제 안 함)
- `output/`: 생성된 MIDI, MusicXML (.xml), PDF 파일
