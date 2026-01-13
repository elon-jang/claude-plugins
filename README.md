# elon-plugins

[AI-Native Product Team](AI_NATIVE_PRODUCT_TEAM.md)을 위한 Claude Code 플러그인 마켓플레이스입니다.

## 설치

### 1. Marketplace 추가

```bash
/plugin marketplace add elon-jang/youtube-to-score
```

### 2. 원하는 플러그인 설치

```bash
# YouTube 피아노 영상 → 악보 변환
/plugin install youtube-to-score@elon-plugins
```

## Plugins

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
elon-plugins/
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
