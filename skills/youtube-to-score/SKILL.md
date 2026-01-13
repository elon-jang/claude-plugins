---
name: youtube-to-score
description: YouTube 피아노 연주 영상에서 자동으로 악보(MIDI, MusicXML, PDF)를 생성하는 도구. 사용자가 "유튜브 피아노 영상을 악보로 만들어줘", "YouTube에서 피아노 채보해줘", "이 유튜브 영상 악보로 변환해줘", "YouTube piano to sheet music" 등을 요청할 때 사용. basic-pitch AI로 오디오를 MIDI로 변환하고 music21 + LilyPond로 악보를 렌더링함.
---

# YouTube-to-Score

YouTube 피아노 연주 영상 → 악보(MIDI, MusicXML, PDF) 자동 생성.

## Command

```
/youtube-to-score <youtube_url>
```

예시:
```
/youtube-to-score https://youtube.com/watch?v=7bSvEVvnOQM
```

## Usage Examples

자연어 요청:
```
"이 유튜브 피아노 영상을 악보로 만들어줘: https://youtube.com/watch?v=xxx"
"YouTube에서 피아노 채보해줘"
"https://youtu.be/xxx 악보로 변환해줘"
```

## Execution

```bash
source venv/bin/activate
python skills/youtube-to-score/scripts/main.py "YOUTUBE_URL"
```

## Scripts

| 스크립트 | 역할 |
|---------|------|
| `scripts/main.py` | 파이프라인 진입점 |
| `scripts/downloader.py` | YouTube → WAV |
| `scripts/transcriber.py` | WAV → MIDI |
| `scripts/renderer.py` | MIDI → XML/PDF |

## Pipeline

```
YouTube URL → Downloader → Transcriber → Renderer
                 ↓              ↓             ↓
            downloads/       output/       output/
             (WAV)          (MIDI)      (XML, PDF)
```

## Output

| 폴더 | 파일 |
|------|------|
| `downloads/` | WAV 오디오 |
| `output/` | MIDI, MusicXML, PDF |

## Constraints

피아노 전용 · macOS 전용 · YouTube URL만 · 최대 10분

## Setup

```bash
./scripts/setup.sh
```
