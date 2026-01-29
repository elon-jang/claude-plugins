# LinkedIn Insight

LinkedIn 글 저장/검색/분석 플러그인.

## 스킬

- `/linkedin-save` - 글 저장
- `/linkedin-search <검색어>` - 검색
- `/linkedin-analyze` - 분석

## 검색 실행

```bash
python scripts/search.py "<검색어>" --mode hybrid --verbose
```

## 저장 위치

- 글: `data/posts/*.md`
- 벡터: `data/chroma/`

## 환경변수

```
GOOGLE_API_KEY=<Gemini API 키>
```
