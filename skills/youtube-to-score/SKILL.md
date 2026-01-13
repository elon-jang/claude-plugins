---
name: youtube-to-score
description: YouTube 피아노 연주 영상에서 자동으로 악보(MIDI, MusicXML, PDF)를 생성하는 도구. 사용자가 "유튜브 피아노 영상을 악보로 만들어줘", "YouTube에서 피아노 채보해줘", "이 유튜브 영상 악보로 변환해줘", "YouTube piano to sheet music" 등을 요청할 때 사용. basic-pitch AI로 오디오를 MIDI로 변환하고 music21 + LilyPond로 악보를 렌더링함.
---

# YouTube-to-Score

YouTube 피아노 연주 영상 → 악보(MIDI, MusicXML, PDF) 자동 생성 CLI 도구.

## Usage Examples

사용자 요청 예시:
```
"이 유튜브 피아노 영상을 악보로 만들어줘: https://youtube.com/watch?v=xxx"
"YouTube에서 피아노 채보해줘"
"https://youtu.be/xxx 악보로 변환해줘"
"YouTube piano to sheet music"
```

## Execution

```bash
# 프로젝트 루트에서 실행
source venv/bin/activate
python skills/youtube-to-score/scripts/main.py "YOUTUBE_URL"
```

개별 모듈:
```bash
python scripts/downloader.py "YOUTUBE_URL"       # downloads/에 WAV
python scripts/transcriber.py audio.wav          # output/에 MIDI
python scripts/renderer.py input.mid output.pdf  # MIDI → XML + PDF
```

## Scripts

| 스크립트 | 역할 |
|---------|------|
| `scripts/main.py` | 파이프라인 통합 진입점 |
| `scripts/downloader.py` | YouTube → WAV (`yt-dlp`) |
| `scripts/transcriber.py` | WAV → MIDI (`basic-pitch`) |
| `scripts/renderer.py` | MIDI → XML/PDF (`music21`) |

## Pipeline

```
YouTube URL → Downloader → Transcriber → Renderer → Output
                 ↓              ↓             ↓
            downloads/       output/       output/
             (WAV)          (MIDI)      (XML, PDF)
```

## Key Details

- `download_audio()` 반환: `(filepath, is_trimmed)` 튜플
- 10분 초과 시 첫 10분만 추출
- 출력 파일명: `_basic_pitch.mid` 접미사 자동 추가
- PDF 렌더링: 임시 디렉토리에서 "score" 파일명으로 LilyPond 실행
- SciPy < 1.15 필수

## Constraints

피아노 전용 · macOS 전용 · YouTube URL만 · 단일 URL · 최대 10분

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install yt-dlp basic-pitch music21 onnxruntime "scipy<1.15"
brew install ffmpeg lilypond
```
