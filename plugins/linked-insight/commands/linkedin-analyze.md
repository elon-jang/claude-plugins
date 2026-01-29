---
name: linkedin-analyze
description: Analyze saved LinkedIn posts for insights, summaries, and tag distribution. Use when users say "linkedin 분석", "인사이트", "포스트 요약", or ask for analysis of saved posts.
argument-hint: ""
allowed-tools:
  - Bash
  - Read
  - Glob
---

# LinkedIn 글 분석

저장된 LinkedIn 글을 분석하고 인사이트를 도출합니다.

## 분석 기능

| 기능 | 설명 |
|------|------|
| 개별 요약 | 특정 글 심층 분석 |
| 종합 분석 | 여러 글 크로스 분석 |
| 태그 분포 | 주제별 분류 통계 |
| 관련 글 추천 | 유사 글 연결 |

## 실행 방법

### 글 목록 조회

```bash
ls <project_root>/data/posts/
```

### 개별 글 읽기

```bash
cat "<project_root>/data/posts/<파일명>.md"
```

### 태그 분포 분석

```bash
cd <project_root>
python -c "
import frontmatter
from pathlib import Path
from collections import Counter

posts = Path('data/posts').glob('*.md')
tags = []
for p in posts:
    post = frontmatter.load(p)
    t = post.get('tags', [])
    tags.extend(t if isinstance(t, list) else [t])

print('=== 태그 분포 ===')
for tag, count in Counter(tags).most_common(20):
    print(f'{tag}: {count}')
"
```

### 관련 글 검색

```bash
python scripts/search.py "<주제>" --mode semantic --limit 5
```

## 분석 워크플로우

1. **범위 결정**: 특정 글 vs 전체
2. **데이터 수집**: 파일 읽기 또는 검색
3. **분석 수행**:
   - 핵심 포인트 추출
   - 공통 주제 식별
   - 트렌드 파악
4. **결과 정리**: 마크다운 포맷으로 출력
5. **액션 제안**: 다음 단계 추천
