# Webfetch Plugin

YouTube 요약 추출 및 Longblack 기사 스크랩을 위한 Claude Code 플러그인입니다.

## Features

- **YouTube 요약**: LiveWiki를 통해 YouTube 영상 요약 추출
- **Longblack 스크랩**: 기사를 Markdown/PDF로 저장
- **오늘의 기사 자동 감지**: 롱블랙 홈페이지에서 오늘의 기사 자동 탐지
- **배치 처리**: 여러 URL 일괄 처리
- **캐시**: URL 기반 캐시로 중복 요청 방지

## Commands

### `/webfetch:webfetch-scrape <url>`
URL을 스크랩하여 Markdown/PDF로 저장합니다.

```bash
/webfetch:webfetch-scrape https://youtu.be/VIDEO_ID
/webfetch:webfetch-scrape https://longblack.co/note/1872
/webfetch:webfetch-scrape https://longblack.co/note/1872 -f pdf
```

### `/webfetch:webfetch-today`
롱블랙 오늘의 기사를 자동으로 찾아 스크랩합니다.

```bash
/webfetch:webfetch-today
```

### `/webfetch:webfetch-batch <file>`
URL 목록 파일에서 여러 URL을 일괄 스크랩합니다.

```bash
/webfetch:webfetch-batch urls.txt
/webfetch:webfetch-batch urls.txt --report report.json
```

### `/webfetch:webfetch-cache`
캐시를 관리합니다.

```bash
/webfetch:webfetch-cache --stats
/webfetch:webfetch-cache --clear
```

## Supported Sites

| Site | URL Pattern | Description |
|------|-------------|-------------|
| YouTube | `youtube.com/watch?v=*`, `youtu.be/*` | LiveWiki 경유 요약 추출 |
| LiveWiki | `livewiki.com/*/content/*` | 직접 스크랩 |
| Longblack | `longblack.co/note/*`, `longblack.co` | 기사 스크랩, 홈페이지 자동 감지 |

## Output

- **기본**: Markdown (.md) + PDF (.pdf) 동시 생성
- **파일명**: `YYYY-MM-DD_제목.ext`
- **출력 위치**: `webfetch/output/`

## Setup

```bash
cd ~/elon/ai/projects/webfetch
npm install
npx playwright install chromium firefox
```

## Daily Automation

cron으로 매일 롱블랙 기사 자동 스크랩:

```bash
0 9 * * * cd ~/elon/ai/projects/webfetch && node src/index.js "https://longblack.co" --skip-existing --no-cache >> ~/logs/webfetch.log 2>&1
```
