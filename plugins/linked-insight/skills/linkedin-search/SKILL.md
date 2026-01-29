---
name: linkedin-search
description: Search saved LinkedIn posts using keyword, semantic, or hybrid search. Use when users say "linkedin 검색", "포스트 찾기", "관련 글", or ask about saved posts.
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

검색 결과를 사용자에게 정리해서 보여줍니다:

1. **제목** (점수)
   - Author: 작성자 | Date: 날짜
   - Tags: 태그들
   - Preview: 미리보기 (verbose 모드)

## 추가 액션

검색 후 제안:
- 특정 글 전체 보기
- 관련 글 더 찾기
- `/linkedin-analyze`로 분석
