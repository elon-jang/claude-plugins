---
name: linkedin-search
description: LinkedIn 글 검색 (키워드/시맨틱/하이브리드)
argument-hint: "<검색어>"
allowed-tools:
  - Bash
  - Read
  - Glob
---

# LinkedIn 글 검색

저장된 LinkedIn 글을 검색합니다.

## 검색 모드

| 모드 | 설명 |
|------|------|
| `hybrid` (기본) | 키워드 + 시맨틱 결합 (RRF) |
| `keyword` | 전문 검색 |
| `semantic` | 임베딩 유사도 검색 |

## 실행 방법

```bash
cd <project_root>
python scripts/search.py "<검색어>" --mode <mode> --limit <n> --verbose
```

### 예시

```bash
# 하이브리드 검색 (기본)
python scripts/search.py "Claude Code"

# 시맨틱 검색
python scripts/search.py "멀티에이전트" --mode semantic

# 키워드 검색 + 미리보기
python scripts/search.py "해커톤" --mode keyword --verbose
```

## 출력 포맷

검색 결과를 사용자에게 마크다운으로 정리해서 보여줍니다:

```markdown
## 검색 결과: "<검색어>"

| # | 제목 | 작성자 | 날짜 | 링크 |
|---|------|--------|------|------|
| 1 | 제목1 | 작성자1 | 날짜1 | [원본](URL) 또는 [파일](경로) |
| 2 | 제목2 | 작성자2 | 날짜2 | [원본](URL) 또는 [파일](경로) |

### 상세 정보

1. **제목1**
   - Tags: 태그들
   - Link: URL (있으면) 또는 File: 파일경로
```

**중요**: 각 결과에 반드시 링크(URL 또는 파일 경로)를 포함합니다.

## 추가 액션

검색 후 제안:
- 특정 글 전체 보기
- 관련 글 더 찾기
- `/linkedin-analyze`로 분석
