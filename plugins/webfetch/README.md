# Webfetch

YouTube 요약 추출 및 Longblack 기사 스크랩을 Markdown/PDF로 저장하는 Claude Code 플러그인입니다.

## 설치

```bash
/plugin marketplace add elon-jang/claude-plugins
/plugin install webfetch@claude-kit
```

### 수동 설치

```bash
git clone https://github.com/elon-jang/claude-plugins.git
cd claude-plugins/plugins/webfetch
```

### 사전 요구사항

webfetch CLI 프로젝트가 설치되어 있어야 합니다:

```bash
cd ~/elon/ai/projects/webfetch
npm install
npx playwright install chromium firefox
```

## 사용법

### 명령어

```
/webfetch:webfetch-scrape <url> [options]    # URL 스크랩 (YouTube/Longblack)
/webfetch:webfetch-today [options]           # 롱블랙 오늘의 기사 자동 스크랩
/webfetch:webfetch-batch <file> [options]    # URL 파일 일괄 처리
/webfetch:webfetch-cache [--stats|--clear]   # 캐시 관리
```

### 작동 방식

1. URL 또는 커맨드를 입력하면 Playwright 브라우저가 실행
2. 로그인이 필요한 사이트는 첫 실행 시 수동 로그인 (세션 자동 저장)
3. 콘텐츠 추출 후 Markdown + PDF로 동시 저장
4. 결과 파일: `output/YYYY-MM-DD_제목.md`, `output/YYYY-MM-DD_제목.pdf`

## 사용 예시

### 1. Longblack 기사 스크랩

```bash
/webfetch:webfetch-scrape https://longblack.co/note/1872

# 결과:
# 📄 webfetch - Longblack
#
# ✓ Saved to: output/2026-01-26_기사_제목.md
# ✓ Saved to: output/2026-01-26_기사_제목.pdf
```

### 2. YouTube 영상 요약 추출

```bash
/webfetch:webfetch-scrape https://youtu.be/Iz26OkoAk0w

# 결과:
# 📄 webfetch - LiveWiki
#
# ✓ Saved to: output/2026-01-26_영상_제목.md
# ✓ Saved to: output/2026-01-26_영상_제목.pdf
```

### 3. 특정 포맷만 출력

```bash
# PDF만
/webfetch:webfetch-scrape https://longblack.co/note/1872 -f pdf

# Markdown만
/webfetch:webfetch-scrape https://longblack.co/note/1872 -f markdown

# JSON (구조화 데이터)
/webfetch:webfetch-scrape https://longblack.co/note/1872 -f json
```

### 4. 오늘의 기사 자동 스크랩

```bash
/webfetch:webfetch-today

# 결과:
# 📄 webfetch - Longblack
#
# Homepage detected. Finding today's article...
# Found: https://longblack.co/note/1875
#
# ✓ Saved to: output/2026-01-26_오늘의_기사_제목.md
# ✓ Saved to: output/2026-01-26_오늘의_기사_제목.pdf
```

**이미 스크랩한 경우:**

```bash
/webfetch:webfetch-today

# 결과:
# 오늘의 기사가 이미 스크랩되어 있습니다:
#   2026-01-26_오늘의_기사_제목.md
#   2026-01-26_오늘의_기사_제목.pdf
```

### 5. 배치 처리

**URL 파일 준비 (`urls.txt`):**

```
# YouTube 영상
https://youtu.be/VIDEO_ID_1
https://youtu.be/VIDEO_ID_2

# Longblack 기사
https://longblack.co/note/1868
https://longblack.co/note/1872
```

```bash
/webfetch:webfetch-batch urls.txt --report report.json

# 결과:
# 📋 Batch mode: 4 URLs from urls.txt
#
# [1/4] ✓ https://youtu.be/VIDEO_ID_1
# [2/4] ✓ https://youtu.be/VIDEO_ID_2
# [3/4] ✓ https://longblack.co/note/1868
# [4/4] ✓ https://longblack.co/note/1872
#
# Total: 4 | Success: 4 | Failed: 0
# Report saved to: report.json
```

### 6. 캐시 관리

```bash
# 캐시 통계 조회
/webfetch:webfetch-cache --stats

# 결과:
# 📦 Cache Statistics
#
#   Entries: 5
#   Size:    128.45 KB
#
#   Recent entries:
#     - https://longblack.co/note/1872
#       Cached: 2026-01-26T09:00:00
#     - https://youtu.be/Iz26OkoAk0w
#       Cached: 2026-01-25T14:30:00
```

```bash
# 캐시 삭제
/webfetch:webfetch-cache --clear

# 결과:
# ✓ Cache cleared
```

## 옵션

### 스크랩 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `-f, --format <type>` | 출력 포맷 (markdown, pdf, json) | md + pdf 동시 |
| `-o, --output <path>` | 저장 경로 지정 | `output/YYYY-MM-DD_제목.ext` |
| `-b, --browser <type>` | 브라우저 (chrome, firefox) | chrome |
| `--headless` | 헤드리스 모드 (로그인 불가) | false |
| `--keep-open` | 스크랩 후 브라우저 유지 (디버깅용) | false |
| `--no-cache` | 캐시 무시, 항상 새로 스크랩 | false |
| `--cache-max-age <hours>` | 캐시 유효기간 (시간) | 24 |
| `--skip-existing` | 오늘 날짜 파일이 있으면 스킵 | false |

### 배치 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--stop-on-error` | 첫 에러 시 중단 | false |
| `--report <path>` | JSON 리포트 저장 경로 | - |
| `--skip-existing` | 이미 스크랩한 URL 스킵 | false |

## 지원 사이트

| Site | URL Pattern | Description |
|------|-------------|-------------|
| YouTube | `youtube.com/watch?v=*`, `youtu.be/*` | LiveWiki 경유 요약 추출 |
| LiveWiki | `livewiki.com/*/content/*` | 직접 스크랩 |
| Longblack | `longblack.co/note/*` | 기사 스크랩 |
| Longblack | `longblack.co` | 홈페이지 → 오늘의 기사 자동 감지 |

## 결과물

| 작업 | 내용 |
|------|------|
| 기본 출력 | `output/YYYY-MM-DD_제목.md` + `.pdf` |
| 포맷 지정 | `output/YYYY-MM-DD_제목.{md,pdf,json}` |
| 배치 리포트 | `report.json` (성공/실패 상세) |
| 캐시 | `.cache/` (URL 해시 기반, 24시간 TTL) |
| 브라우저 세션 | `auth/chrome-profile/` (로그인 유지) |

## 일일 자동화 (Cron)

매일 오전 9시 롱블랙 오늘의 기사 자동 스크랩:

```bash
0 9 * * * cd ~/elon/ai/projects/webfetch && node src/index.js "https://longblack.co" --skip-existing --no-cache >> ~/logs/webfetch.log 2>&1
```

- `--skip-existing`: 오늘 날짜 파일이 이미 있으면 스킵
- `--no-cache`: 항상 새로 스크랩 (캐시 무시)

## 트러블슈팅

### 로그인 실패
```
Error: Login required
→ auth/ 폴더 삭제 후 재실행: rm -rf auth/chrome-profile/
→ --keep-open 플래그로 브라우저 상태 확인
```

### 콘텐츠 추출 실패
```
Error: Could not find article content
→ 사이트 구조 변경 가능성 → --keep-open으로 페이지 확인
→ adapter CONFIG 셀렉터 업데이트 필요
```

### 네트워크 에러
```
Error: net::ERR_ABORTED
→ 자동 3회 재시도 (exponential backoff)
→ 재실행으로 해결되는 경우가 대부분
```

## 제한 사항

- Playwright 브라우저가 설치되어 있어야 함
- 로그인 필요 사이트는 첫 실행 시 수동 로그인 필요
- 헤드리스 모드에서는 로그인 불가

## 라이선스

MIT License

## 관련 문서

- [CLAUDE.md](./CLAUDE.md) - 개발자 가이드
