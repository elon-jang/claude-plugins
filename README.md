# YouTube Sound to Score

YouTube 동영상의 음악을 분석하여 자동으로 악보(PDF, MusicXML, MIDI)를 만들어주는 도구입니다.

## 주요 기능

- **유튜브 음원 추출**: `yt-dlp`를 사용하여 고음질 WAV 추출.
- **AI 자동 채보**: Spotify의 `basic-pitch` AI를 사용하여 음악을 MIDI로 변환.
- **악보 렌더링**: `music21` 및 `LilyPond`를 사용하여 전문가 수준의 PDF 및 MusicXML 생성.

## Claude Plugin 설치

이 프로젝트는 Claude Code 플러그인으로 사용할 수 있습니다.

### GitHub에서 설치 (Marketplace)

```bash
# GitHub 저장소에서 직접 설치
/plugins marketplace add yourname/youtube-to-score
```

### 로컬 설치

```bash
# 프로젝트 디렉토리에서 플러그인 설치
claude plugins add /path/to/youtube-to-score
```

또는 Claude Code 실행 중 `/plugins add /path/to/youtube-to-score` 명령어로 설치합니다.

### 사용법

플러그인 설치 후 Claude Code에서 자연어로 요청하면 자동으로 스킬이 트리거됩니다:

```
"이 유튜브 피아노 영상을 악보로 만들어줘: https://youtube.com/watch?v=..."
"YouTube에서 피아노 채보해줘"
"유튜브 피아노 영상 악보로 변환해줘"
```

### 플러그인 관리

```bash
# 설치된 플러그인 목록 확인
claude plugins list

# 플러그인 제거
claude plugins remove youtube-to-score
```

## Marketplace 등록 (배포)

이 플러그인을 다른 사용자들이 설치할 수 있도록 Marketplace에 등록하는 방법입니다.

### 1. GitHub 저장소 생성

```bash
# Git 초기화 및 커밋
git init
git add .
git commit -m "Initial commit: YouTube-to-Score plugin"

# GitHub 저장소 연결
git remote add origin https://github.com/yourname/youtube-to-score.git
git push -u origin main
```

### 2. plugin.json 설정

`.claude-plugin/plugin.json` 파일을 수정합니다:

```json
{
  "name": "youtube-to-score",
  "version": "1.0.0",
  "description": "YouTube 피아노 연주 영상에서 악보를 자동 생성",
  "author": {
    "name": "Your Name",
    "email": "your@email.com"
  },
  "repository": "https://github.com/yourname/youtube-to-score",
  "homepage": "https://github.com/yourname/youtube-to-score",
  "license": "MIT",
  "keywords": ["youtube", "piano", "sheet-music", "midi"]
}
```

### 3. 사용자 설치 방법 안내

저장소 URL을 공유하면 다른 사용자가 설치할 수 있습니다:

```bash
# GitHub에서 설치
/plugins marketplace add yourname/youtube-to-score

# GitLab 또는 다른 Git 호스트
/plugins marketplace add https://gitlab.com/yourname/youtube-to-score.git
```

### 4. 버전 관리

Semantic Versioning을 사용합니다:

| 버전 | 설명 |
|------|------|
| MAJOR (1.x.x) | 호환되지 않는 변경 |
| MINOR (x.1.x) | 새로운 기능 추가 |
| PATCH (x.x.1) | 버그 수정 |

```bash
# 버전 업데이트 후 배포
git tag v1.0.1
git push origin v1.0.1
```

### 5. 멀티 플러그인 Marketplace (선택)

여러 플러그인을 하나의 Marketplace로 관리하려면:

```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    ├── youtube-to-score/
    └── other-plugin/
```

`marketplace.json`:
```json
{
  "name": "my-marketplace",
  "owner": {
    "name": "Your Name",
    "email": "your@email.com"
  },
  "plugins": [
    {
      "name": "youtube-to-score",
      "source": "./plugins/youtube-to-score",
      "description": "YouTube 피아노 영상 → 악보 변환",
      "version": "1.0.0"
    }
  ]
}
```

## 수동 설치 및 실행

### 1. 시스템 의존성 설치 (macOS)

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

### 3. 실행

```bash
python skills/youtube-to-score/scripts/main.py "YOUR_YOUTUBE_URL"
```

## 결과물

- `downloads/`: 추출된 오디오 파일 (`.wav`)
- `output/`: 생성된 악보 파일 (`.mid`, `.xml`, `.pdf`)

## 기술 스택

| 구성 요소 | 기술 |
|----------|------|
| Engine | Spotify Basic Pitch (Neural Network) |
| Transcription | Polyphonic (다성 음악 지원) |
| Rendering | LilyPond Engraving |

## 제한 사항

- 피아노 전용 (다른 악기 미지원)
- macOS 전용
- 최대 10분 길이

## 라이선스

MIT License
