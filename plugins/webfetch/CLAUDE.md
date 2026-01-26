# Webfetch Plugin - Developer Guide

## Overview

webfetch는 YouTube 요약(LiveWiki 경유) 및 Longblack 기사를 스크랩하여 Markdown/PDF로 저장하는 CLI 도구의 Claude Code 플러그인입니다.

## Plugin Structure

```
plugins/webfetch/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── commands/
│   ├── webfetch-scrape.md   # Single URL scrape
│   ├── webfetch-today.md    # Today's Longblack article
│   ├── webfetch-batch.md    # Batch processing
│   └── webfetch-cache.md    # Cache management
├── skills/
│   └── webfetch-assistant/
│       └── SKILL.md         # Auto-activation skill
├── CLAUDE.md                # This file
└── README.md                # User guide
```

## Commands

| Command | Description |
|---------|-------------|
| `webfetch-scrape` | URL 스크랩 (YouTube/LiveWiki/Longblack) |
| `webfetch-today` | 롱블랙 오늘의 기사 자동 스크랩 |
| `webfetch-batch` | URL 파일 일괄 처리 |
| `webfetch-cache` | 캐시 관리 (통계/삭제) |

## Key Dependencies

- **webfetch project**: `~/elon/ai/projects/webfetch`
- **Node.js**: CLI 실행
- **Playwright**: 브라우저 자동화 (chromium, firefox)
- **Commander.js**: CLI 프레임워크

## Architecture

플러그인은 webfetch CLI를 호출하는 래퍼입니다:
- Commands → `node src/index.js` 호출
- Skill → 자연어 요청을 적절한 command로 라우팅

### Adapter Pattern
webfetch는 사이트별 adapter를 사용:
- `livewiki.js` - YouTube/LiveWiki 스크랩
- `longblack.js` - Longblack 기사 스크랩
- 새 사이트 추가: `/src/adapters/`에 adapter 구현

### Output Format
- 기본: Markdown + PDF 동시 생성
- 파일명: `YYYY-MM-DD_제목.ext`
- 출력 디렉토리: `output/`

## Adding New Commands

1. `commands/` 에 새 `.md` 파일 생성
2. YAML frontmatter 포함 (name, description, argument-hint, allowed-tools)
3. Workflow 단계별 설명
4. 필요시 SKILL.md에 트리거 조건 추가

## Troubleshooting

### 브라우저 프로필 문제
```bash
# 세션 초기화
rm -rf ~/elon/ai/projects/webfetch/auth/chrome-profile/
```

### Playwright 설치
```bash
cd ~/elon/ai/projects/webfetch && npx playwright install chromium firefox
```
