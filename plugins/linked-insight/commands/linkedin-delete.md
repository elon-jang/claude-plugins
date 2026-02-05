---
name: linkedin-delete
description: LinkedIn 글 삭제 (파일 + 벡터DB)
argument-hint: "<파일명>"
allowed-tools:
  - Bash
  - Read
  - Glob
  - AskUserQuestion
---

# LinkedIn 글 삭제

저장된 LinkedIn 글을 파일 시스템과 ChromaDB에서 동시에 삭제합니다.

## 실행 방법

### 글 목록 조회

```bash
cd <project_root>
python scripts/delete.py --list
```

### 글 삭제

```bash
# 파일명으로 삭제 (확인 프롬프트 표시)
python scripts/delete.py "파일명.md"

# 확인 없이 삭제
python scripts/delete.py "파일명.md" --force

# 미리보기 (실제 삭제 안함)
python scripts/delete.py "파일명.md" --dry-run
```

## 동작 흐름

1. 파일명으로 대상 파일 검색 (부분 매칭 지원)
2. 복수 매칭 시 목록 표시 후 중단
3. 삭제 확인 (--force 없으면)
4. ChromaDB에서 embedding_id로 벡터 삭제
5. 파일 시스템에서 마크다운 파일 삭제

## 출력 예시

```
✓ Deleted: Claude Code 팁.md
  - ChromaDB: removed (Claude Code 팁-abc123)
```

## 주의사항

- 삭제는 되돌릴 수 없습니다
- 확실하지 않으면 `--dry-run`으로 먼저 확인하세요
- 복수 파일 삭제 시 하나씩 실행하세요
