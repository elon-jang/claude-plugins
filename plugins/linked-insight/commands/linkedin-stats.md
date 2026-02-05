---
name: linkedin-stats
description: LinkedIn 글 통계 조회
argument-hint: "[--json]"
allowed-tools:
  - Bash
  - Read
---

# LinkedIn 글 통계

저장된 LinkedIn 글의 통계를 조회합니다.

## 실행 방법

```bash
cd <project_root>
python scripts/stats.py
```

### JSON 출력

```bash
python scripts/stats.py --json
```

## 출력 정보

| 항목 | 설명 |
|------|------|
| 총 글 수 | 저장된 전체 글 개수 |
| 태그 분포 | 고유 태그 수, 태그 커버리지, Top 10 |
| 작성자 분포 | 고유 작성자 수, Top 5 |
| URL 커버리지 | 원본 URL이 있는 글 비율 |
| 컨텐츠 길이 | 평균/최소/최대 글자 수 |

## 출력 예시

```markdown
## LinkedIn Posts 통계

**총 24개 글**

### 태그
- 고유 태그: 15개
- 태그 있는 글: 8개 (33.3%)
- Top 10:
  - `claude-code`: 5
  - `ai`: 4
  ...

### 작성자
- 고유 작성자: 3명
- 작성자 있는 글: 12개 (50.0%)
```
