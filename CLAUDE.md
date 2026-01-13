# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube 피아노 연주 영상 → 악보(MIDI, MusicXML, PDF) 자동 생성 CLI 도구.

## Commands

```bash
# Setup (자동)
./scripts/setup.sh

# Setup (수동)
brew install ffmpeg lilypond
python3 -m venv venv && source venv/bin/activate
pip install yt-dlp basic-pitch music21 onnxruntime "scipy<1.15"

# Run
python skills/youtube-to-score/scripts/main.py "YOUTUBE_URL"
```

## Architecture

선형 3단계 파이프라인: `Downloader → Transcriber → Renderer`

| 스크립트 | 역할 | 핵심 라이브러리 |
|---------|------|----------------|
| `scripts/downloader.py` | YouTube → WAV | `yt-dlp` |
| `scripts/transcriber.py` | WAV → MIDI | `basic-pitch` (ONNX) |
| `scripts/renderer.py` | MIDI → XML/PDF | `music21`, LilyPond |

## Key Implementation Details

- **10분 제한**: `download_audio()` → `(filepath, is_trimmed)` 튜플 반환
- **한글 오류**: `_get_korean_error_message()`로 yt-dlp 오류 변환
- **SciPy 패치**: `scipy.signal.gaussian` 호환성 패치 (transcriber.py:7-8)
- **PDF 렌더링**: 임시 디렉토리에서 "score" 파일명으로 LilyPond 실행

## Constraints

피아노 전용 · macOS 전용 · YouTube URL만 · 단일 URL · 최대 10분

## Plugin Structure

```
.claude-plugin/plugin.json
skills/youtube-to-score/
├── SKILL.md
└── scripts/
    ├── main.py
    ├── downloader.py
    ├── transcriber.py
    └── renderer.py
```
