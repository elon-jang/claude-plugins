# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube 피아노 연주 영상 → 악보(MIDI, MusicXML, PDF) 자동 생성 CLI 도구 및 Claude Code 플러그인.

## Commands

```bash
# Setup
./scripts/setup.sh

# Run (CLI)
source venv/bin/activate
python skills/youtube-to-score/scripts/main.py "YOUTUBE_URL"

# Run (Claude Code command)
/youtube-to-score <youtube_url>
```

## Architecture

선형 3단계 파이프라인: `Downloader → Transcriber → Renderer`

| 스크립트 | 역할 | 라이브러리 |
|---------|------|-----------|
| `downloader.py` | YouTube → WAV | `yt-dlp` |
| `transcriber.py` | WAV → MIDI | `basic-pitch` |
| `renderer.py` | MIDI → XML/PDF | `music21`, LilyPond |

## Key Implementation Details

- **경고 억제**: `warnings.filterwarnings` + `no_warnings` 옵션
- **10분 제한**: `download_audio()` → `(filepath, is_trimmed)` 튜플 반환
- **한글 오류**: `_get_korean_error_message()`로 yt-dlp 오류 변환
- **SciPy 패치**: `scipy.signal.gaussian` 호환성 패치
- **PDF 렌더링**: MuseScore → LilyPond 폴백

## Constraints

피아노 전용 · macOS 전용 · YouTube URL만 · 최대 10분

## Plugin Structure

```
.claude-plugin/plugin.json
commands/youtube-to-score.md      # /youtube-to-score 명령
scripts/setup.sh                   # 설치 스크립트
skills/youtube-to-score/
├── SKILL.md
└── scripts/
    ├── main.py
    ├── downloader.py
    ├── transcriber.py
    └── renderer.py
```
