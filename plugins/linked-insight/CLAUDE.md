# LinkedIn Insight

LinkedIn 글 저장/검색/분석 플러그인.

## 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/linkedin-save` | 글 저장 (메타검증 + 중복체크 + URL단축 + 임베딩) |
| `/linkedin-search <검색어>` | 하이브리드 검색 |
| `/linkedin-analyze` | 글 분석/인사이트 |
| `/linkedin-stats` | 통계 조회 |
| `/linkedin-delete <파일명>` | 글 삭제 |

## CLI

```bash
# 글 가져오기 (URL → JSON)
python scripts/fetch_post.py "https://www.linkedin.com/posts/..." --verbose

# 검색
python scripts/search.py "<검색어>" --mode hybrid --verbose

# 통계
python scripts/stats.py

# 삭제
python scripts/delete.py --list
python scripts/delete.py "파일명.md"

# URL 단축
python scripts/shorten_urls.py --file "data/posts/파일명.md" --verbose
python scripts/shorten_urls.py "긴 URL이 포함된 텍스트"

# 데이터 정비 (backfill)
python scripts/backfill.py --dry-run    # 미리보기
python scripts/backfill.py --apply      # 자동 수정 적용 (태그/날짜/파일명)
python scripts/backfill.py --report     # 수동 처리 필요 항목만
python scripts/backfill.py --notes-report  # AI Notes 형식 현황
```

## 저장 위치

- 글: `data/posts/*.md`
- 벡터: `data/chroma/`

## 환경변수

```
GOOGLE_API_KEY=<Gemini API 키>
BITLY_TOKEN=<Bitly API 토큰>  # URL 단축용 (선택)
LINKEDIN_COOKIE_PATH=<linkedin_cookie.json 경로>  # 글 가져오기용 (선택, 기본값 있음)
```
