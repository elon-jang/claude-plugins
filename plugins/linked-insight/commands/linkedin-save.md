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

1. **소스 감지** → 롱블랙 URL / LinkedIn URL / 수동 입력 분기
2. **메타데이터 검증** (author 빈값/slug 확인)
3. **중복 체크** (URL + 제목 + 시맨틱 검색)
4. AI 태그 생성 (최소 3개 필수)
5. frontmatter 포함 마크다운 파일 저장
6. **URL 단축** (BITLY_TOKEN 있으면 자동 실행)
7. Gemini 임베딩 생성 → ChromaDB 저장

## 실행 방법

### Step 0: 소스 감지 및 콘텐츠 가져오기

사용자 입력을 분석하여 소스를 판별합니다.

#### A. 롱블랙 (longblack.co)

**감지 조건** (우선순위 1):
- URL에 `longblack.co` 포함 → 해당 기사 스크래핑
- 인자가 "롱블랙"이거나 인자 없이 "롱블랙" 언급 → 오늘의 기사 (`https://longblack.co`)

webfetch CLI로 스크래핑:
```bash
# 특정 기사
node /Users/elon/elon/ai/projects/webfetch/src/index.js "<longblack URL>" -f markdown -o "/tmp/longblack_tmp.md"

# 오늘의 기사 (홈페이지 → 자동 탐색)
node /Users/elon/elon/ai/projects/webfetch/src/index.js "https://longblack.co" -f markdown -o "/tmp/longblack_tmp.md"
```

- **성공 시**: `/tmp/longblack_tmp.md`에서 frontmatter의 `title`, `url`과 본문 content 추출 → Step 2로 진행
  - author: "롱블랙" 고정
  - source: "longblack"
- **실패 시**: 에러 메시지를 사용자에게 보여주고 중단 (로그인 필요 등)

> **주의**: 브라우저가 열릴 수 있음. 로그인이 필요하면 브라우저에서 직접 로그인 후 자동 진행됨.

#### B. LinkedIn URL

**감지 조건** (우선순위 2): `linkedin.com/posts/...` 또는 `linkedin.com/feed/update/...`

```bash
cd <project_root>
python scripts/fetch_post.py "<LinkedIn URL>" --verbose
```

- **성공 시**: JSON 출력에서 `title`, `author`, `content`, `url` 추출 → Step 2로 진행
- **실패 시**: 에러 메시지 출력 후 사용자에게 수동 입력 안내 (Step 0-C로 이동)

#### C. 수동 입력

LinkedIn URL이 아니고 롱블랙도 아닌 경우 (또는 B 실패 시):

사용자에게 요청:
- 글 내용 (필수)
- 작성자 이름 (**권장** - 비어있으면 검색 품질 저하)
- 원본 URL (**권장** - 중복 체크 및 출처 추적용)
- 추가 태그 (선택)

### Step 1: 메타데이터 검증

추출된 메타데이터를 검증합니다.

- **author가 빈 문자열이면** → AskUserQuestion으로 반드시 사용자에게 작성자 이름 질문. 빈 문자열 저장 금지.
- **author가 URL slug 형태이면** (예: `john-doe-123abc`) → 사용자에게 실명 확인 후 수정.

### Step 2: 중복 체크

저장 전 기존 글과 중복 확인:

```bash
cd <project_root>
# URL로 중복 체크
grep -l "url: \"<입력된URL>\"" data/posts/*.md 2>/dev/null

# 제목으로 유사 글 검색
python scripts/search.py "<제목 일부>" --mode keyword --limit 3

# 시맨틱 중복 검색 (본문 첫 30자로 유사도 확인)
python scripts/search.py "<본문 첫 30자>" --mode semantic --limit 3
```

유사도 80% 이상 결과가 있으면 의심 중복으로 사용자에게 확인.
중복 발견 시 사용자에게 확인 후 진행.

### Step 3: AI 태그 생성

글 내용을 분석하여 태그 **반드시 3-5개** 자동 생성:
- 기존 태그 참고: `python scripts/stats.py --json | jq '.tags.top_10'`
- 주요 카테고리: `claude-code`, `ai-tools`, `productivity`, `development`, `career`, `startup`
- **태그 0개 상태로 Step 4 진행 금지.** 최소 3개 태그를 생성해야 함.

### Step 4: 파일 생성

```python
# 파일 저장 위치
<project_root>/data/posts/<제목>.md
```

파일 포맷:
```markdown
---
title: "{제목 - 50자 이내로 정제}"
author: "{작성자}"
date: "{YYYY-MM-DD}"
url: "{URL}"
tags: [tag1, tag2, tag3]
embedding_id: "{unique-id}"
---

{원본 내용}

---
## AI Notes
- **Summary**: {1-2문장 요약}
- **Topics**: {태그 나열}
```

### Step 5: URL 단축

BITLY_TOKEN이 `.env`에 설정되어 있으면 긴 URL을 자동 단축합니다.
이미 짧은 URL (bit.ly, lnkd.in, youtu.be, t.co 등)은 건너뜁니다.

```bash
cd <project_root>
python scripts/shorten_urls.py --file "data/posts/<파일명>.md" --verbose
```

BITLY_TOKEN이 없으면 이 단계를 건너뛰고 다음으로 진행합니다.

### Step 6: 임베딩 생성

```bash
cd <project_root>
python scripts/migrate.py --file "data/posts/<파일명>.md"
```

## 출력

저장 완료 시:
- 파일 경로
- embedding_id
- 저장된 태그
- (중복 체크 결과)
