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

1. $ARGUMENTS 첫 단어 → 서브커맨드, 나머지 → 옵션 (예: `blog --publish` → 서브커맨드 `blog`, 옵션 `--publish`)
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
6. Git commit & push

---

## blog - 블로그 글 저장/조회/수정

`/spark blog` → 새 글 작성 (기본)
`/spark blog --publish` → 새 글 작성 + 즉시 발행
`/spark blog list` → 블로그 목록 조회
`/spark blog update` → 기존 글 수정

### 블로그 스타일

| Style | 톤 | Claude 다듬기 가이드 |
|-------|----|--------------------|
| essay | 생각의 흐름, 1인칭 서술 | 자연스러운 문체, 단락 구분, 도입-전개-마무리 |
| tutorial | 단계별 설명, 코드 예시 중심 | 번호 매긴 단계, 코드 블록, 명확한 지시문 |
| opinion | 논점 명확, 근거 제시 | 주장-근거-반론-결론 구조, 강한 어조 |
| til | 짧고 핵심만, 오늘 배운 것 | 3~10줄, 배운 것 + 왜 중요한지 |
| linkedin | 짧고 임팩트, 훅→스토리→교훈 | 첫 줄 훅, 짧은 문단, 줄바꿈 많이, CTA나 질문으로 마무리 |
| x-post | 280자 압축, 날카로운 한 줄 | 핵심 한 문장 + 부연 1~2줄, thread 형식 가능 |
| free | 톤 조정 없이 원문 그대로 | Claude가 내용을 다듬지 않고 그대로 저장 |

**스타일 결정 순서**: `--style` 인자 → `.sparks/config.json`의 `blog.defaultStyle` → AskUserQuestion (선택 후 config에 저장)

### 새 글 작성 (기본)

1. `mkdir -p blog`
2. AskUserQuestion 2회:
   - 1차: Style(위 표 선택지), Title, Tags
   - 2차: Content (핵심 내용, 키워드, 메모 수준 OK — `free` 외에는 Claude가 스타일에 맞게 다듬음)
3. 파일: `blog/YYYY-MM-DD-{title}.md` (Common 파일명 규칙 적용)
   - frontmatter: `title, date, style, tags` 포함
4. Git commit & push
5. 성공 메시지에 `/spark add`로 지식 연결 안내

### 새 글 작성 + 즉시 발행 (`--publish`)

1~4는 새 글 작성과 동일
5. AskUserQuestion: "공개/비공개?" (1. 공개 2. 비공개)
6. Git commit & push 완료 후, publish 플로우 자동 실행 (`--files {filename}` 또는 `--files {filename}:private`)
7. 성공 메시지에 배포 URL 포함

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

Git commit & push.

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

`/spark publish` → 저장된 글 중 선택하여 배포 (기본)
`/spark publish --all` → 모든 blog/*.md 배포
`/spark publish --draft` → 대화 내용을 저장 없이 바로 배포

**Manifest**: `.sparks/published.json` — 발행 항목 배열. 각 항목은 `{ "file": "name.md", "access": "public"|"private" }`. (`--draft`는 manifest에 추가하지 않음)

**접근 제어**:
- `public`: 누구나 접근 가능 (`/posts/` 경로)
- `private`: Cloudflare Access 인증 필요 (`/private/posts/` 경로)
- 파일 선택 시 AskUserQuestion으로 공개/비공개 선택

**공통 플로우** (1~3단계는 모든 모드 공통):

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

### 기본 모드 (저장된 글 배포)

4. 파일 선택 + 접근 권한:
   - `--all`: 모든 blog/*.md (기존 manifest의 access 유지, 새 파일은 public)
   - `--files {file}`: 특정 파일 (`:private` 접미사로 비공개 지정, 예: `글.md:private`)
   - 파일명만 지정 (예: `publish 글.md`): AskUserQuestion으로 "공개/비공개" 선택
   - 인자 없음: AskUserQuestion으로 파일 선택 후 "공개/비공개" 선택
5. 빌드 실행 (**published.json을 직접 편집하지 않음** — `--files` 플래그가 manifest 추가를 자동 처리):
   ```bash
   node {PLUGIN_DIR}/scripts/build-blog.mjs --source {REPO_ROOT}/blog --output {REPO_ROOT}/.sparks/_build --manifest {REPO_ROOT}/.sparks/published.json --config {REPO_ROOT}/.sparks/config.json --files {file}:{access}|--all
   ```
   - 빌드 결과: `/posts/` (공개) + `/private/posts/` (비공개) + 인덱스 각 1개
6. Cloudflare Pages 배포:
   ```bash
   wrangler pages deploy {REPO_ROOT}/.sparks/_build --project-name {publish.projectName} --branch {publish.branch} --commit-dirty=true
   ```
   - wrangler 출력에서 Environment 확인 → "Preview"가 포함되면 경고: "⚠ Preview 환경에 배포되었습니다. Production 배포를 위해 config의 publish.branch를 확인하세요."
7. 성공 메시지 표시:
   - `publish.url`이 설정되어 있으면 해당 URL 표시, 없으면 wrangler 출력에서 URL 추출하여 표시
   - 공개/비공개 글 수 각각 표시
   - 비공개 글 있으면: "비공개 글은 {url}/private/ 에서 접근 (Cloudflare Access 설정 필요)"
8. 빌드 디렉토리 정리:
   ```bash
   rm -rf {REPO_ROOT}/.sparks/_build
   ```
9. Git commit & push (manifest 변경 반영):
   ```bash
   cd {REPO_ROOT} && git add .sparks/published.json && git commit -m "publish: {title} 발행" && git push origin {CURRENT_BRANCH}
   ```

### --draft 모드 (대화 내용 → 저장 없이 배포)

대화에서 작성한 블로그 글을 `blog/`에 저장하지 않고 바로 배포. manifest(`published.json`)에도 추가하지 않음.

4. 대화에서 블로그 글 내용 추출 (가장 최근 작성한 블로그 형식의 텍스트)
5. AskUserQuestion: "제목을 입력하세요" (대화에서 제목 추론 가능하면 기본값 제시)
6. 임시 파일 생성:
   ```
   {REPO_ROOT}/.sparks/_draft/YYYY-MM-DD-{title}.md
   ```
7. 빌드 실행 (임시 파일 + 기존 manifest 합산):
   ```bash
   node {PLUGIN_DIR}/scripts/build-blog.mjs --source {REPO_ROOT}/blog --output {REPO_ROOT}/.sparks/_build --manifest {REPO_ROOT}/.sparks/published.json --config {REPO_ROOT}/.sparks/config.json --draft {REPO_ROOT}/.sparks/_draft/YYYY-MM-DD-{title}.md
   ```
   - `--draft`: manifest에 추가하지 않고 임시 파일을 포함하여 빌드
8. Cloudflare Pages 배포 (기본 모드와 동일)
9. 정리:
   ```bash
   rm -rf {REPO_ROOT}/.sparks/_draft {REPO_ROOT}/.sparks/_build
   ```
10. 성공 메시지 + 안내: "영구 저장하려면 `/spark blog`로 저장하세요"

**에러 처리**: wrangler 미설치 시 `npm install -g wrangler` 안내. 인증 실패 시 `wrangler login` 안내.

**Cloudflare Access 설정 (최초 1회, 수동)**:
Dashboard > Zero Trust > Access > Applications > Add > Self-hosted
- Application URL: `{publish.url}/private/*`
- Policy: 본인 이메일 허용

---

## init - 저장소 초기화

**인자**: `[directory]` (기본: 현재 디렉토리)

1. 확인 질문 → 이미 `.sparks/` 있으면 리셋 여부 확인
2. 디렉토리 생성: `concepts/ insights/ skills/ til/ blog/ .sparks/`
3. 파일 생성:
   - `.sparks/config.json`: version, categories, defaultCategory, leitnerIntervals, socraticLevels, publish (projectName, branch, url, title, description)
   - `.sparks/progress.json`: `{}`
   - `.gitignore`: progress.json, .DS_Store, editor files
   - `README.md`: 저장소 소개 (제목, 설명)
4. Git init (아직 아니면) → 초기 커밋 여부 확인
5. `~/.sparks/config.json`에 `defaultRepo` 저장
