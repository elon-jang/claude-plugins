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

# 애플리케이션 단축키 관리 + Leitner Box 학습
/plugin install shortcut@ai-plugins

# 지식/인사이트 저장 + 학습
/plugin install sparks@ai-plugins

# YouTube/Longblack 스크랩
/plugin install webfetch@ai-plugins

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

### [shortcut](plugins/shortcut/)

애플리케이션 단축키를 GitHub에 저장하고 Leitner Box 시스템으로 학습하는 플러그인입니다.

**사용법**: `/shortcut-init`, `/shortcut-add`, `/shortcut-learn`, `/shortcut-search`

**주요 기능**:

- 대화형 단축키 추가 (App, Category, Shortcut, Description)
- Leitner Box 알고리즘 학습 (Box 1→2→3)
- 키워드 검색 및 앱별 필터링
- A4 Cheat Sheet HTML 생성
- Git 자동 커밋

### [sparks](plugins/sparks/)

지식과 인사이트를 Github에 저장하고 다양한 학습 모드로 학습하는 플러그인입니다.

**사용법**: `/spark-init`, `/spark-add`, `/spark-blog`, `/spark-learn`, `/spark-search`, `/spark-stats`

**주요 기능**:

- 지식/인사이트 저장 (YAML frontmatter + Q&A 자동 생성)
- 블로그 글 저장 및 지식 연결
- 3가지 학습 모드: Socratic, Flashcard (Leitner 5-box), Connect
- 학습 통계 대시보드
- Git 자동 커밋

### [webfetch](plugins/webfetch/)

YouTube 요약 및 Longblack 기사를 스크랩하여 Markdown/PDF로 저장하는 플러그인입니다.

**사용법**: `/webfetch-scrape`, `/webfetch-today`, `/webfetch-batch`, `/webfetch-cache`

**주요 기능**:

- YouTube 영상 요약 추출 (LiveWiki 경유)
- Longblack 기사 스크랩
- Markdown + PDF 동시 저장
- 배치 처리 및 캐시 관리
- 오늘의 기사 자동 감지

**사전요구사항**: Playwright 브라우저 설치

### [youtube-to-score](plugins/youtube-to-score/)

YouTube 피아노 연주 영상에서 악보(MIDI, MusicXML, PDF)를 자동 생성하는 플러그인입니다.

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
│   ├── add-prompt/
│   ├── linked-insight/
│   ├── shortcut/
│   ├── sparks/
│   ├── webfetch/
│   └── youtube-to-score/
└── README.md
```

## Blog

<!-- spark-index:blog -->
- [2026-01-21] [[Playwright] 삭제 버튼 52번 누르기 싫어서 만든 자동화 스크립트](blog/2026-01-21-playwright-delete-automation.md)

## 라이선스

MIT
