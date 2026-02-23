---
name: spark
description: 지식 저장/학습/검색 통합 명령 (add, blog, log, learn, search, list, stats, publish, init)
argument-hint: "<add|blog|log|learn|search|list|stats|publish|init> [options]"
allowed-tools:
  - AskUserQuestion
  - Glob
  - Read
  - Write
  - Edit
  - Bash
---

# Spark - 지식/인사이트 통합 명령

## Routing

1. $ARGUMENTS 첫 단어 → 서브커맨드, 나머지 → 옵션
2. 서브커맨드 없으면 AskUserQuestion으로 선택 (add/blog/log/learn/publish 우선 표시, 나머지는 "Other" 선택 시)

## Common Patterns

### 저장소 경로 결정 (모든 서브커맨드 공통)

1. `$ARGUMENTS`에 `> {path}` 가 있으면 해당 경로 사용
2. 없으면 `~/.sparks/config.json`의 `defaultRepo` 읽기
3. 없으면 현재 디렉토리에서 `git rev-parse --show-toplevel` 시도
4. 모두 실패 → **첫 사용 설정 플로우**:
   - AskUserQuestion: "Sparks 저장소 경로를 입력하세요" (예: ~/elon/ai/my-sparks)
   - 입력된 경로에 `.sparks/config.json` 존재 확인
     - 있으면 → `~/.sparks/config.json`에 `defaultRepo` 저장
     - 없으면 → "저장소가 초기화되지 않았습니다. 초기화할까요?" → `/spark init {path}` 실행 후 `defaultRepo` 저장

**`~/.sparks/config.json`** (유저 글로벌 설정):
```json
{ "defaultRepo": "~/elon/ai/my-sparks" }
```

경로 결정 후:
- `REPO_ROOT` = 확정된 저장소 경로
- `git branch --show-current` → CURRENT_BRANCH

### 파일명 규칙

- 제목을 그대로 파일명에 사용 (한글 유지)
- 공백 → 하이픈(`-`), 특수문자(`/\:*?"<>|`) 제거
- 예: "플러그인 커맨드 작성 원칙" → `플러그인-커맨드-작성-원칙.md`
- blog: `YYYY-MM-DD-{title}.md` (예: `2026-02-14-플러그인-커맨드-작성-원칙.md`)
- 중복 시 `-2`, `-3` 부여

### 기타 공통

**카테고리**: concepts(이론), insights(깨달음), skills(실용), til(오늘 배운 것), blog(블로그+로그)

**Knowledge File Frontmatter**:
```yaml
---
id: "{timestamp}-{random}"
title: "{title}"
category: "{category}"
tags: [tag1, tag2]
created: "{ISO timestamp}"
source: "{source}"
blog_link: null
confidence: 3
connections: []
review_count: 0
last_reviewed: null
---
```

**README.md 업데이트 패턴**:
- `<!-- spark-index:{category} -->` 앵커 검색 → 없으면 `## {Category}` 검색
- 섹션 없으면 새로 생성
- 항목 추가: `- [{title}]({category}/{filename}.md)` (알파벳순 or 최신순)

**Git commit & push**: `git add {files} && git commit -m "{msg}" && git push origin {CURRENT_BRANCH}`

---

## add - 지식/인사이트 저장

1. 카테고리 디렉토리 자동 감지 (없으면 기본 4개 사용)
2. `blog/` 존재 시 Source에 "From blog post" 옵션 추가 → 선택하면 최근 4개 블로그 목록 표시
3. AskUserQuestion 2회:
   - 1차: Category, Title, Tags, Source
   - 2차: Content, Key Points
4. Claude가 Q&A 2-3개 자동 생성 → 사용자 확인
5. `{category}/{filename}.md` 생성 (Common 파일명 규칙 + frontmatter 템플릿 사용)
   - blog_link 있으면 제목 아래 `> **Blog**: [{title}](../{blog_link})` 추가
6. README.md 업데이트 → Git commit & push

---

## blog - 블로그 글 저장/조회/수정

`/spark blog` → 새 글 작성 (기본)
`/spark blog list` → 블로그 목록 조회
`/spark blog update` → 기존 글 수정

### 새 글 작성 (기본)

1. `mkdir -p blog`
2. AskUserQuestion: Title, Tags → Content (2회)
3. 파일: `blog/YYYY-MM-DD-{title}.md` (Common 파일명 규칙 적용)
   - 태그 있으면 YAML frontmatter 포함, 없으면 `# {title}` + 본문
4. README.md Blog 섹션에 `- [{date}] [{title}](blog/{filename})` 추가 (최신순)
   - Blog 섹션 없으면 TIL 섹션 뒤에 생성
5. Git commit & push
6. 성공 메시지에 `/spark add`로 지식 연결 안내

### 목록 조회 (`blog list`)

1. `blog/*.md` Glob → frontmatter의 title, date, tags 파싱
2. 날짜 역순으로 번호 매겨 표시:
   ```
   Blog Posts (3 posts today, 38 total)

   [Today]
   1. 플러그인 커맨드 작성 원칙 (claude-code, plugin)
   2. 로컬에서 다 잡고 배포하자 (devops, docker)

   [2026-02-13]
   3. AI 네이티브 시대, 개발자에게 진짜 필요한 것 (ai, career)
   ...
   ```
3. `--date=YYYY-MM-DD` 또는 `--date=today` 로 날짜 필터 가능

### 기존 글 수정 (`blog update`)

1. `blog list` 와 동일하게 번호 매긴 목록 표시
2. AskUserQuestion: "수정할 글 번호를 선택하세요" (최근 4개 옵션)
3. 선택된 파일 Read → 현재 내용 표시
4. AskUserQuestion: "어떻게 수정할까요?"
   - "내용 추가" → 기존 내용 끝에 append
   - "내용 교체" → 새 내용으로 대체
   - "Claude에게 맡기기" → 사용자 지시사항 입력받아 Claude가 수정
5. Edit로 파일 수정 → Git commit & push

**자연어 지원**: "오늘 블로그 조회해줘" → `blog list --date=today`, "2번 글 업데이트해줘" → `blog update` (2번 자동 선택)

---

## log - 데일리 로그

**옵션**: `--style=diary|bullet|devlog|narrative`

**스타일 결정 순서**: --style 인자 → `.sparks/config.json`의 `log.defaultStyle` → AskUserQuestion (선택 후 config에 저장)

| Style | 톤 |
|-------|----|
| diary | 1인칭 일기체, 감정 포함 |
| bullet | 글머리 기호 목록, 핵심만 |
| devlog | Problem → Solution → Result |
| narrative | 관찰자 시점 서술 |

**파일**: `blog/YYYY-MM-DD-daily-log.md`

- **새 파일**: frontmatter(`title, date, style, tags:[daily], episodes:1`) + `# YYYY-MM-DD Daily Log` + 에피소드
- **기존 파일**: episodes 카운트 +1, 파일 끝에 `---` 구분선 + 에피소드 append

**에피소드 형식**:
```markdown
## HH:MM - {Claude가 생성한 짧은 제목}

{스타일에 맞게 다듬은 내용, 3-10줄}
```

README.md에 오늘 로그 이미 있으면 skip, 없으면 추가. Git commit & push.

---

## learn - 학습 모드

**옵션**: `--mode=socratic|flashcard|connect`, `--category=<name>`, `--all`

모드 미지정 시 AskUserQuestion으로 선택.

**공통 준비**: 카테고리별 .md 파일 읽기 → frontmatter 파싱 → `.sparks/progress.json` 로드

### Socratic (소크라틱 대화)

낮은 confidence 또는 미복습 항목 선택 후 5단계 질문:
1. **Explain**: 자기 말로 설명
2. **Why**: 왜 중요한지
3. **How**: 실제 적용 방법
4. **Edge Cases**: 예외 상황
5. **Connections**: 다른 개념과 연결

답변 평가: Strong → 다음 레벨 + confidence↑ / Partial → 힌트 후 재시도 / Weak → 설명 제공

### Flashcard (Leitner 5-box)

| Box | Interval |
|-----|----------|
| 1 | 1일 |
| 2 | 3일 |
| 3 | 7일 |
| 4 | 14일 |
| 5 | 30일 |

due 카드 필터 → Q 표시 → A 공개 → 자기 평가(Correct: box+1, Incorrect: box→1) → progress.json 업데이트 → 세션 요약

### Connect (연결 탐색)

항목 선택 → 태그 Jaccard similarity > 0.3 기준 유사 항목 탐색 → 관계 유형 선택(Prerequisite/Builds on/Contrasts/Synthesizes) → Synthesizes면 새 인사이트 생성 제안(`/spark add`) → 양쪽 frontmatter connections 업데이트

**Progress 파일** (`.sparks/progress.json`):
```json
{ "{item_id}": { "box": 2, "lastReviewed": "ISO", "correctCount": 5, "incorrectCount": 1 } }
```

---

## search - 검색

**인자**: `<keyword> --tag=<tag> --category=<cat>`

1. 카테고리 지정 시 해당 디렉토리만, 아니면 전체 (.sparks, blog, README 제외)
2. 각 파일 frontmatter 파싱 후 매칭:
   - Title match: +10점, Tag match: +5점/개, Content match: +1점/회(max 10)
3. 점수순 결과 표시: title, category, tags, confidence, match reason
4. 결과 없으면 대안 검색 제안

---

## list - 목록 조회

**옵션**: `--category=<name>`, `--stats`, `--due`

- **기본**: 카테고리별 항목 목록 + 총 개수
- **--stats**: 테이블 형식 (Title, Confidence, Reviews, Box, Last Review)
- **--due**: Leitner interval 기준 복습 예정 항목만 표시

---

## stats - 학습 통계 대시보드

모든 knowledge 파일(.sparks, blog, README 제외) 파싱 후 표시:
- **카테고리 분포**: 막대 그래프 (########)
- **Confidence 분포**: Level 1~5별 아이템 수
- **복습 현황**: Never / 1-2x / 3-5x / 6+x
- **Due for Review**: Overdue / Due today / Due this week
- **Top Tags**: 빈도순 상위 10개
- **Blog 통계** (blog/ 존재 시): 총 포스트, knowledge 연결 비율, 이번 달 포스트 수

---

## publish - 블로그 배포

blog/ 디렉토리의 MD 파일을 HTML로 빌드하여 Cloudflare Pages에 배포.

**Manifest**: `.sparks/published.json` — 발행된 파일명 배열. publish 할 때마다 선택한 파일이 추가됨.

**플로우**:

1. 저장소 경로 결정 (Common Patterns) → `REPO_ROOT`
2. 배포 설정 읽기:
   - `{REPO_ROOT}/.sparks/config.json`의 `publish` 섹션 읽기
   - `publish.projectName`이 null이면 → AskUserQuestion: "Cloudflare Pages 프로젝트 이름을 입력하세요" → config에 저장
   - `publish.branch`: 기본 "master" (Cloudflare Pages production 브랜치)
   - `publish.url`: 배포 후 표시할 URL (null이면 wrangler 출력에서 URL 추출)
3. 의존성 설치 (최초 1회):
   ```bash
   cd {PLUGIN_DIR} && npm install --silent
   ```
   - `PLUGIN_DIR` = 이 플러그인의 디렉토리 (`plugins/sparks/`)
4. 빌드 실행 (manifest 기반 — 발행된 글만 빌드+인덱스):
   ```bash
   node {PLUGIN_DIR}/scripts/build-blog.mjs --source {REPO_ROOT}/blog --output {REPO_ROOT}/.sparks/_build --manifest {REPO_ROOT}/.sparks/published.json --config {REPO_ROOT}/.sparks/config.json --files {files}|--all
   ```
   - `--files`: 선택한 파일을 manifest에 추가 후 전체 manifest 빌드
   - `--all`: 모든 blog/*.md를 manifest에 등록 후 빌드
5. Cloudflare Pages 배포:
   ```bash
   wrangler pages deploy {REPO_ROOT}/.sparks/_build --project-name {publish.projectName} --branch {publish.branch} --commit-dirty=true
   ```
   - wrangler 출력에서 Environment 확인 → "Preview"가 포함되면 경고: "⚠ Preview 환경에 배포되었습니다. Production 배포를 위해 config의 publish.branch를 확인하세요."
6. 성공 메시지 표시:
   - `publish.url`이 설정되어 있으면 해당 URL 표시, 없으면 wrangler 출력에서 URL 추출하여 표시
   - 발행된 글 수
7. 빌드 디렉토리 정리:
   ```bash
   rm -rf {REPO_ROOT}/.sparks/_build
   ```

**에러 처리**: wrangler 미설치 시 `npm install -g wrangler` 안내. 인증 실패 시 `wrangler login` 안내.

---

## init - 저장소 초기화

**인자**: `[directory]` (기본: 현재 디렉토리)

1. 확인 질문 → 이미 `.sparks/` 있으면 리셋 여부 확인
2. 디렉토리 생성: `concepts/ insights/ skills/ til/ blog/ .sparks/`
3. 파일 생성:
   - `.sparks/config.json`: version, categories, defaultCategory, leitnerIntervals, socraticLevels, publish (projectName, branch, url, title, description)
   - `.sparks/progress.json`: `{}`
   - `.gitignore`: progress.json, .DS_Store, editor files
   - `README.md`: 카테고리별 섹션 + `<!-- spark-index:{cat} -->` 앵커
4. Git init (아직 아니면) → 초기 커밋 여부 확인
5. `~/.sparks/config.json`에 `defaultRepo` 저장
