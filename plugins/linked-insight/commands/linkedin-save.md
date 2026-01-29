---
name: linkedin-save
description: LinkedIn 글 저장 및 벡터 인덱싱
argument-hint: ""
allowed-tools:
  - AskUserQuestion
  - Glob
  - Read
  - Write
  - Edit
  - Bash
---

# LinkedIn 글 저장

LinkedIn 글을 저장하고 벡터 인덱싱합니다.

## 동작 흐름

1. 사용자에게 LinkedIn 글 내용 입력 요청
2. 메타데이터 추출 (제목, 작성자, 날짜, 해시태그, URL)
3. frontmatter 포함 마크다운 파일 저장
4. Gemini 임베딩 생성 → ChromaDB 저장

## 실행 방법

### Step 1: 글 내용 수집

사용자에게 요청:
- LinkedIn 글 내용 (필수)
- 작성자 이름 (선택)
- 원본 URL (선택)
- 추가 태그 (선택)

### Step 2: 파일 생성

```python
# 파일 저장 위치
<project_root>/data/posts/<제목>.md
```

파일 포맷:
```markdown
---
title: "{제목}"
author: "{작성자}"
date: "{YYYY-MM-DD}"
url: "{URL}"
tags: [tag1, tag2]
embedding_id: "{unique-id}"
---

{원본 내용}

---
## AI Notes
- **Summary**: {1-2문장 요약}
- **Topics**: {태그 나열}
```

### Step 3: 임베딩 생성

```bash
cd <project_root>
python scripts/migrate.py --file "data/posts/<파일명>.md"
```

## 출력

저장 완료 시:
- 파일 경로
- embedding_id
- 저장된 태그
