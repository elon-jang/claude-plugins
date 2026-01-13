# YouTube Sound to Score

YouTube 동영상의 음악을 분석하여 자동으로 악보(PDF, MusicXML, MIDI)를 만들어주는 도구입니다.

## 주요 기능

- **유튜브 음원 추출**: `yt-dlp`를 사용하여 고음질 WAV 추출.
- **AI 자동 채보**: Spotify의 `basic-pitch` AI를 사용하여 음악을 MIDI로 변환.
- **악보 렌더링**: `music21` 및 `LilyPond`를 사용하여 전문가 수준의 PDF 및 MusicXML 생성.

## 설치 방법

### 1. 시스템 의존성 설치 (macOS)

이 도구는 오디오 처리 및 악보 렌더링을 위해 다음 프로그램이 필요합니다.

```bash
brew install ffmpeg lilypond
```

### 2. 프로젝트 설정

```bash
# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install yt-dlp basic-pitch music21 onnxruntime "scipy<1.15"
```

## 사용법

가상환경이 활성화된 상태에서 `main.py`에 유튜브 URL을 전달하여 실행합니다.

```bash
python main.py "YOUR_YOUTUBE_URL"
```

### 결과물 확인

- `downloads/`: 추출된 오디오 파일 (`.wav`)
- `output/`: 생성된 악보 파일 (`.mid`, `.xml`, `.pdf`)

## 기술 스택

- **Engine**: Spotify Basic Pitch (Neural Network)
- **Transcription**: Polyphonic (다성 음악 지원)
- **Rendering**: LilyPond Engraving
