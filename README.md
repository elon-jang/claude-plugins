# claude-plugins

[AI-Native Product Team](AI_NATIVE_PRODUCT_TEAM.md)을 위한 Claude Code 플러그인 마켓플레이스입니다.

## 설치

### 1. Marketplace 추가

```bash
/plugin marketplace add elon-jang/claude-plugins
```

### 2. 원하는 플러그인 설치

```bash
# AI 프롬프트 자동 추가 및 Git 푸시
/plugin install add-prompt@ai-plugins

# YouTube 피아노 영상 → 악보 변환
/plugin install youtube-to-score@ai-plugins
```

## Plugins

### [add-prompt](plugins/add-prompt/)

AI 프롬프트 저장소에 새로운 프롬프트를 추가하고 자동으로 Git에 푸시하는 플러그인입니다.

**사용법**: `/add-prompt`

**주요 기능**:

- 대화형 프롬프트 생성 워크플로우
- 자동 파일명 생성 (kebab-case)
- README 자동 업데이트 (알파벳순 정렬)
- Git commit 및 push 자동화
- 중복 파일명 처리

### [youtube-to-score](plugins/youtube-to-score/skills/youtube-to-score/SKILL.md)

YouTube 피아노 연주 영상에서 악보(MIDI, MusicXML, PDF)를 자동 생성하는 스킬입니다.

**사용법**: `/youtube-to-score <youtube_url>`

**주요 기능**:

- YouTube 영상에서 오디오 추출 (yt-dlp)
- 오디오를 MIDI로 변환 (basic-pitch)
- MIDI를 MusicXML/PDF 악보로 렌더링 (music21, LilyPond)

**제약사항**:

- 피아노 전용
- macOS 전용
- 최대 10분 영상

## Marketplace 구조

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── youtube-to-score/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/youtube-to-score/
│           ├── SKILL.md
│           └── scripts/
└── README.md
```

## 라이선스

MIT
