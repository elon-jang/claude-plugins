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

# LinkedIn 글 저장/검색/분석
/plugin install linked-insight@ai-plugins

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

### [linked-insight](plugins/linked-insight/)

LinkedIn 글을 저장하고 시맨틱 검색하는 플러그인입니다.

**사용법**: `/linkedin-save`, `/linkedin-search`, `/linkedin-analyze`

**주요 기능**:

- LinkedIn 글 저장 (frontmatter + Gemini 임베딩)
- 하이브리드 검색 (키워드 + 시맨틱)
- 글 분석 및 인사이트 도출
- ChromaDB 벡터 저장소

**환경변수**: `GOOGLE_API_KEY` (Gemini API)

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
│   ├── linked-insight/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/{linkedin-save,linkedin-search,linkedin-analyze}/
│   │   ├── scripts/
│   │   └── data/posts/
│   └── youtube-to-score/
│       ├── .claude-plugin/plugin.json
│       └── skills/youtube-to-score/
└── README.md
```

## Blog

<!-- spark-index:blog -->
- [2026-01-21] [[Playwright] 삭제 버튼 52번 누르기 싫어서 만든 자동화 스크립트](blog/2026-01-21-playwright-delete-automation.md)

## 라이선스

MIT
