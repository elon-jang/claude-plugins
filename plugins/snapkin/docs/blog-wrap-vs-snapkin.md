# Claude Code 세션 관리의 두 가지 철학: session-wrap vs Snapkin

> 코딩 세션을 마칠 때마다 "오늘 뭐 했더라?"를 고민하지 않으려면 어떻게 해야 할까요? 두 플러그인이 제시하는 서로 다른 해답을 깊이 탐구합니다.

---

## 들어가며: 왜 세션 관리가 필요한가?

Claude Code로 3시간 동안 열심히 코딩했습니다. 버그 3개를 고치고, 새 기능을 추가했고, 중요한 아키텍처 결정도 내렸습니다. 그런데...

```
# 다음 날 아침
$ claude
> 어제 뭐 하다 말았더라?
```

git log를 뒤지고, 코드를 훑어보고, 기억을 더듬어봅니다. 15분이 지났습니다. 이제야 어제의 컨텍스트가 떠오릅니다.

**이 15분을 0분으로 만들 수 있다면?**

session-wrap과 Snapkin은 이 문제를 해결하기 위해 탄생했습니다. 같은 목표, 다른 접근법. 이 글에서는 두 플러그인의 구조, 철학, 그리고 언제 무엇을 써야 하는지 깊이 있게 비교해봅니다.

---

## Part 1: 구조 비교 — 설계 철학의 차이

### session-wrap: "분석 후 제안" 아키텍처

session-wrap은 **5개의 전문 에이전트**가 각자의 관점에서 세션을 분석하고, 결과를 종합해서 **사용자에게 제안**합니다.

```
┌─────────────────────────────────────────────────────────────┐
│  /wrap 실행                                                  │
├─────────────────────────────────────────────────────────────┤
│  Step 1: Git Status 확인                                    │
├─────────────────────────────────────────────────────────────┤
│  Step 2: Phase 1 — 4개 분석 에이전트 (병렬 실행)              │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ doc-updater │ automation- │ learning-   │ followup-   │  │
│  │             │ scout       │ extractor   │ suggester   │  │
│  │ "문서 뭐    │ "자동화할   │ "오늘 뭘    │ "다음에     │  │
│  │  업데이트?" │  거 없나?"  │  배웠지?"   │  뭐 하지?"  │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
│                           ↓                                  │
├─────────────────────────────────────────────────────────────┤
│  Step 3: Phase 2 — 검증 에이전트 (순차 실행)                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              duplicate-checker                          ││
│  │              "중복 제안 없나 확인"                        ││
│  └─────────────────────────────────────────────────────────┘│
│                           ↓                                  │
├─────────────────────────────────────────────────────────────┤
│  Step 4: 결과 통합 및 사용자에게 표시                         │
├─────────────────────────────────────────────────────────────┤
│  Step 5: 사용자 선택 (AskUserQuestion)                       │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [ ] 커밋 생성                                           ││
│  │ [ ] CLAUDE.md 업데이트                                  ││
│  │ [ ] 자동화 생성 (skill/command/agent)                   ││
│  │ [ ] 건너뛰기                                            ││
│  └─────────────────────────────────────────────────────────┘│
│                           ↓                                  │
├─────────────────────────────────────────────────────────────┤
│  Step 6: 선택된 작업만 실행                                  │
└─────────────────────────────────────────────────────────────┘
```

**핵심 특징**: 에이전트들은 **분석만** 합니다. 파일을 직접 수정하지 않습니다. 모든 변경은 사용자 승인 후 오케스트레이터가 실행합니다.

#### session-wrap 에이전트 상세

| 에이전트 | 역할 | 도구 | 출력 |
|----------|------|------|------|
| **doc-updater** | CLAUDE.md, context.md 업데이트 분석 | Read, Glob, Grep | "이 내용을 CLAUDE.md에 추가하세요" |
| **automation-scout** | 자동화 기회 탐지 | Read, Glob, Grep | "이 패턴을 skill로 만들면 좋겠어요" |
| **learning-extractor** | 학습 포인트 추출 | Read, Glob, Grep | "오늘 배운 것: TIL 형식" |
| **followup-suggester** | 후속 작업 제안 | Read, Glob, Grep | "다음 세션에 할 일: P0-P3" |
| **duplicate-checker** | 중복 제안 검증 | Read, Glob, Grep | "이 제안은 이미 문서화되어 있음" |

---

### Snapkin: "직접 쓰기" 아키텍처

Snapkin은 **3개의 에이전트**가 각자 담당 파일에 **직접 작성**하고, 검증 후 **자동 커밋**합니다.

```
┌─────────────────────────────────────────────────────────────┐
│  Mode Selection                                              │
│  /snapkin | /snapkin quick [msg] | /snapkin review          │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: Dispatch (데이터 수집)                             │
│  - git diff (마지막 sync 커밋부터)                           │
│  - CLAUDE.md, LESSONS.md 읽기                               │
│  - 세션 요약 생성                                            │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: Parallel Scribble (병렬 쓰기)                      │
│  ┌───────────────────┐  ┌───────────────────┐               │
│  │     historian     │  │      auditor      │               │
│  │                   │  │                   │               │
│  │  LESSONS.md에     │  │  CLAUDE.md에      │               │
│  │  직접 작성        │  │  직접 작성        │               │
│  │                   │  │                   │               │
│  │ "오늘 배운 것     │  │ "세션 컨텍스트    │               │
│  │  6개 카테고리로   │  │  완전 재작성,     │               │
│  │  분류해서 저장"   │  │  P0-P3 우선순위"  │               │
│  └───────────────────┘  └───────────────────┘               │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: Validate (검증)                                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    validator                             ││
│  │                    (read-only)                           ││
│  │                                                          ││
│  │  - 보안 스캔 (API 키, 비밀번호)                          ││
│  │  - 구조 검증 (마커, 필수 섹션)                           ││
│  │  - 중복 탐지                                             ││
│  │  - 사이즈 체크 (40줄, 10개 제한)                         ││
│  └─────────────────────────────────────────────────────────┘│
│                           ↓                                  │
│  이슈 발견 시 → 오케스트레이터가 즉시 수정                   │
├─────────────────────────────────────────────────────────────┤
│  Phase 3.5: User Review (review 모드만)                      │
│  "커밋할까요? / diff 보기 / 건너뛰기"                        │
├─────────────────────────────────────────────────────────────┤
│  Phase 4: Snap-Commit (자동 커밋)                            │
│  git add CLAUDE.md LESSONS.md                               │
│  git commit -m "docs: snapkin session sync ..."             │
└─────────────────────────────────────────────────────────────┘
```

**핵심 특징**: 에이전트들이 **직접 파일을 작성**합니다. 엄격한 파일 소유권(historian → LESSONS.md, auditor → CLAUDE.md)으로 충돌을 방지하고, 검증 후 자동 커밋합니다.

#### Snapkin 에이전트 상세

| 에이전트 | 역할 | 소유 파일 | 모델 | 도구 |
|----------|------|-----------|------|------|
| **historian** | 레슨 추출 및 기록 | LESSONS.md | Sonnet | Read, Write, Edit, Grep, Glob |
| **auditor** | 컨벤션 + 세션 컨텍스트 | CLAUDE.md | Sonnet | Read, Write, Edit, Grep, Glob, Bash |
| **validator** | 품질 검증 (읽기 전용) | 없음 | Haiku | Read, Grep, Glob |

---

### 구조 비교 요약

```
                session-wrap                    Snapkin

에이전트 수     5개                             3개
파일 소유권     없음 (모두 읽기 전용)           엄격함 (1:1 매핑)
파일 쓰기       오케스트레이터만                에이전트가 직접
커밋            사용자 선택 후 실행             자동 (review 모드 제외)
검증 시점       Phase 2 (쓰기 전)               Phase 3 (쓰기 후)
대상 파일       CLAUDE.md, context.md, 기타     CLAUDE.md, LESSONS.md (고정)
```

---

## Part 2: 기능별 장단점 심층 비교

### 2.1 문서 업데이트

#### session-wrap 방식

```markdown
# doc-updater가 분석한 결과 예시

## Documentation Update Analysis

### CLAUDE.md Updates

**Section**: ## Development Environment

**Content to Add:**
```markdown
### New Dependencies
- `@tanstack/query` v5.0 — 데이터 페칭
- `zod` — 런타임 유효성 검사
```

**Rationale**: package.json에 새 의존성 2개 추가됨.
다음 세션에서 이 라이브러리들의 용도를 알아야 함.

**Location**: "## Development Environment" 아래 추가

**Duplicate Check**: 기존 Dependencies 섹션에 없음
```

사용자가 이 제안을 보고 "CLAUDE.md 업데이트" 옵션을 선택하면, 오케스트레이터가 실제로 파일을 수정합니다.

**장점**:
- 변경 전에 정확히 무엇이 추가될지 확인 가능
- 잘못된 제안을 걸러낼 수 있음
- context.md도 지원 (프로젝트별 컨텍스트)

**단점**:
- 매번 "이거 괜찮아?" 확인 필요
- 제안이 길면 읽기 부담

#### Snapkin 방식

```markdown
# auditor가 직접 작성한 CLAUDE.md Session Context

<!-- SNAPKIN:SESSION_CONTEXT_START -->
## Session Context

> Current state snapshot. Fully rewritten each session sync by the auditor agent.

### Last Sync

- **Date**: 2026-02-05
- **Session**: API 인증 모듈 구현 및 테스트

### Active Work

- JWT 토큰 검증 미들웨어 구현 완료
- 리프레시 토큰 로직 80% 완료 (저장소 연동 남음)
- 인증 실패 시 에러 응답 형식 정의

### Blockers

- Redis 연결 설정 미완료 — 리프레시 토큰 저장소 필요

### Next Entry Point

- **[P1]** 리프레시 토큰 저장소 연동 — `src/auth/token-store.ts:23`
- **[P2]** 인증 API 통합 테스트 작성 — `tests/auth/`
- **[P3]** 로그아웃 엔드포인트 구현

### Recent Changes

- `src/auth/jwt.ts` — JWT 검증 미들웨어 추가
- `src/auth/refresh.ts` — 리프레시 토큰 로직 (진행 중)
- `src/types/auth.ts` — 인증 관련 타입 정의

### Key Files

```
src/auth/jwt.ts          — JWT 검증 핵심 로직
src/auth/refresh.ts      — 리프레시 토큰 (진행 중)
src/middleware/auth.ts   — Express 미들웨어
tests/auth/jwt.test.ts   — JWT 테스트
```
<!-- SNAPKIN:SESSION_CONTEXT_END -->
```

auditor는 이 내용을 **묻지 않고 바로 작성**합니다. 검증은 나중에 validator가 합니다.

**장점**:
- 빠름 — 확인 과정 없이 바로 작성
- 일관된 포맷 — 항상 같은 구조
- P0-P3 우선순위로 다음 할 일이 명확

**단점**:
- 잘못 작성되면 나중에 수정해야 함
- context.md 미지원 (CLAUDE.md에 통합)

---

### 2.2 학습 기록

#### session-wrap 방식

```markdown
# learning-extractor 분석 결과 예시

## Session Learning Extraction

### Technical Discoveries

#### Express middleware 실행 순서
**What:** middleware는 등록 순서대로 실행됨
**Context:** 인증 미들웨어가 라우터보다 먼저 등록되어야 함
**Key Insight:** app.use() 순서가 곧 실행 순서

**Code Example:**
```javascript
// 올바른 순서
app.use(authMiddleware);  // 1. 먼저 인증
app.use('/api', router);  // 2. 그다음 라우팅

// 잘못된 순서 (인증 안 됨!)
app.use('/api', router);
app.use(authMiddleware);
```

### Mistakes & Lessons

#### JWT 만료 시간 설정 실수
**What went wrong:** 토큰 만료를 '15m' 대신 15로 설정해서 15초 만에 만료
**Symptoms:** "로그인하자마자 로그아웃됨"
**Root cause:** jsonwebtoken의 expiresIn은 숫자면 초 단위
**Lesson:** 항상 문자열로 명시 ('15m', '1h', '7d')
```

이 내용은 사용자가 확인 후 원하는 곳에 저장하거나 복사합니다. 별도의 전용 파일에 자동 저장되지 않습니다.

**장점**:
- 매우 상세한 분석 (실패 원인, 디버깅 과정까지)
- TIL(Today I Learned) 형식으로 공유하기 좋음
- 다양한 카테고리 (Technical, Problem-Solving, Domain, Process, Mistakes)

**단점**:
- 전용 저장소가 없어서 매번 어디에 저장할지 고민
- 히스토리 추적이 어려움

#### Snapkin 방식

```markdown
# historian이 LESSONS.md에 직접 작성

---

## 2026-02-05

- **[Error-Fix]** JWT 만료 시간에 숫자 15 대신 문자열 '15m' 사용해야 함 — jsonwebtoken의 expiresIn은 숫자면 초 단위로 해석됨.
- **[Insight]** Express middleware는 app.use() 등록 순서대로 실행됨 — 인증 미들웨어를 라우터보다 먼저 등록해야 보호됨.
- **[Decision]** 리프레시 토큰 저장소로 Redis 선택 — 인메모리 DB라 빠르고, TTL 지원으로 만료 처리가 간편.
- **[Domain]** JWT의 세 부분: header.payload.signature — header는 알고리즘, payload는 클레임, signature는 검증용.
- **[Future]** Automation candidate: 토큰 검증 테스트가 반복됨 — 인증 테스트 헬퍼 함수 만들기 고려.
```

historian은 6개의 고정 카테고리로 분류해서 LESSONS.md에 **직접 추가**합니다.

**장점**:
- 전용 파일(LESSONS.md)에 자동 축적
- 날짜별로 정리되어 히스토리 추적 용이
- 간결한 한 줄 형식으로 스캔하기 쉬움
- 중복 자동 체크 (같은 내용 재추가 방지)

**단점**:
- session-wrap보다 상세도가 낮음
- 코드 예시가 길면 한 줄에 담기 어려움

---

### 2.3 자동화 발견

#### session-wrap 방식

```markdown
# automation-scout 분석 결과 예시

## Automation Opportunity Analysis

### High Priority

#### JWT Auth Test Helper

**Type:** Skill

**Detected Pattern:**
- Frequency: 5회 반복 (이번 세션)
- Workflow: 토큰 생성 → 테스트 요청 → 응답 검증
- Tools used: jwt.sign, supertest, assertion

**Current Pain:**
- 매 테스트마다 토큰 생성 코드 반복
- 테스트 파일마다 같은 설정 복사
- 만료된 토큰 테스트 케이스 작성이 번거로움

**Proposed Solution:**

```typescript
// .claude/skills/auth-test-helper/
// Usage: /auth-test create-token --user=admin --expires=1h

export function createTestToken(options: {
  user: string;
  role?: string;
  expires?: string;
}) {
  return jwt.sign(
    { sub: options.user, role: options.role || 'user' },
    process.env.JWT_SECRET,
    { expiresIn: options.expires || '1h' }
  );
}

export function createExpiredToken(user: string) {
  return jwt.sign({ sub: user }, process.env.JWT_SECRET, { expiresIn: '-1s' });
}
```

**Expected Benefits:**
- Time saved: 테스트당 2-3분 → 10초
- Error reduction: 토큰 설정 실수 방지
- Consistency: 모든 테스트가 같은 헬퍼 사용

**Implementation Priority:** High
```

이 제안을 보고 사용자가 "자동화 생성"을 선택하면 `/plugin-dev:create-plugin`으로 연결됩니다.

**장점**:
- 구체적인 구현 템플릿까지 제공
- Skill/Command/Agent 중 최적의 형태 추천
- 기존 자동화와 중복 검사

**단점**:
- 즉시 생성되지 않음 (별도 작업 필요)
- 복잡한 자동화는 템플릿만으로 부족

#### Snapkin 방식

```markdown
# historian이 LESSONS.md에 기록

- **[Future]** Automation candidate: 토큰 검증 테스트가 반복됨 — 인증 테스트 헬퍼 함수 만들기 고려.
- **[Future]** Automation candidate: DB 마이그레이션이 스키마 변경 후 항상 수동 실행됨 — pre-commit hook 또는 npm script로 자동화 고려.
```

Snapkin은 자동화 후보를 `[Future]` 태그로 **기록만** 합니다.

**장점**:
- LESSONS.md에 축적되어 나중에 한꺼번에 처리 가능
- 오버헤드 없음 (분석 에이전트 별도 실행 안 함)

**단점**:
- 구현 템플릿 없음
- Skill/Command/Agent 분류 없음
- 기록만 하고 실행으로 연결 안 됨

---

### 2.4 후속 작업 관리

#### session-wrap 방식

```markdown
# followup-suggester 분석 결과 예시

## P1 - High Priority (Should Do Soon)

### 리프레시 토큰 저장소 연동

**Category:** Feature

**Description:** Redis 연결 설정 후 리프레시 토큰 저장/조회/삭제 로직 구현

**Context:** 현재 refresh.ts는 토큰 생성만 하고 저장 안 함.
Redis 없이는 토큰 무효화가 불가능해서 보안 취약점.

**Specific Steps:**
1. Redis 클라이언트 설정 (`src/lib/redis.ts`)
2. TokenStore 인터페이스 정의 (`src/auth/token-store.ts`)
3. RedisTokenStore 구현
4. refresh.ts에서 TokenStore 주입
5. 토큰 무효화 테스트 작성

**Done Criteria:**
- [ ] Redis 연결 성공
- [ ] 토큰 저장/조회/삭제 동작
- [ ] 토큰 만료 시 자동 삭제 (Redis TTL)
- [ ] 통합 테스트 통과

**Related Files:**
- `src/auth/refresh.ts`
- `src/lib/redis.ts` (new)
- `src/auth/token-store.ts` (new)

**Dependencies:** 없음

**Expected Effort:** Medium (2-3시간)

**Priority:** P1

**Impact:** High (보안 취약점 해결)
```

followup-suggester는 매우 상세한 태스크 명세를 제공합니다.

**장점**:
- 프로젝트 관리 수준의 태스크 정의
- Done Criteria로 완료 기준 명확
- 의존성과 예상 시간까지 포함
- TODO/FIXME/WIP 주석 자동 스캔

**단점**:
- 정보량이 많아 읽기 부담
- 간단한 세션에도 과도한 분석

#### Snapkin 방식

```markdown
# auditor가 작성한 Next Entry Point

### Next Entry Point

- **[P1]** 리프레시 토큰 저장소 연동 — `src/auth/token-store.ts:23`
- **[P2]** 인증 API 통합 테스트 작성 — `tests/auth/`
- **[P3]** 로그아웃 엔드포인트 구현
```

Snapkin은 P0-P3 우선순위와 파일 경로만 간결하게 기록합니다.

**장점**:
- 한눈에 스캔 가능
- 파일 경로로 바로 이동 가능
- 5개 제한으로 핵심만 유지

**단점**:
- 상세 컨텍스트 부족
- Done Criteria 없음
- 예상 시간 없음

---

### 2.5 검증 및 보안

#### session-wrap 방식

session-wrap은 **중복 검증**에 집중합니다:

```markdown
# duplicate-checker 결과 예시

## Phase 2 Validation Results

### Merge Recommended

#### doc-updater: "Redis 의존성 추가"

**Phase 1 Proposal:**
```
### Dependencies
- `redis` — 토큰 저장소
```

**Existing Content:** `CLAUDE.md` line 45
```
### Dependencies
- `ioredis` — Redis 클라이언트 (더 나은 TypeScript 지원)
```

**Conclusion:** 이미 ioredis가 문서화됨.
redis 패키지 대신 ioredis 사용 중. 제안 스킵 권장.
```

**특징**: 쓰기 **전에** 중복을 걸러냅니다.

#### Snapkin 방식

Snapkin validator는 **쓰기 후** 다양한 검증을 수행합니다:

```markdown
# validator 검증 항목

## Check 1: Security Scan

검색 패턴:
- API[_-]?KEY|api[_-]?key + 실제 값
- PASSWORD|password + 실제 값
- sk-[a-zA-Z0-9]{20,}
- ghp_[a-zA-Z0-9]{20,}
- SECRET + 실제 값

발견 시 → [REDACTED]로 자동 교체

## Check 2: Session Context Structure

확인 항목:
1. SNAPKIN:SESSION_CONTEXT_START 마커
2. SNAPKIN:SESSION_CONTEXT_END 마커
3. 필수 섹션: Last Sync, Active Work, Blockers, Next Entry Point, Recent Changes, Key Files
4. Last Sync 날짜 = 오늘
5. Next Entry Point에 P0-P3 태그 최소 1개

## Check 3: Duplicate Detection

- LESSONS.md: 같은 내용 중복 (>80% 단어 일치)
- CLAUDE.md: 반복된 규칙, 모순 정보

## Check 4: Size Limits

- Session Context: 40줄 초과 시 경고
- Recent Changes: 10개 초과 시 경고
- Key Files: 10개 초과 시 경고
```

**특징**: 쓰기 **후에** 보안/구조/중복/사이즈를 검증합니다. 문제 발견 시 오케스트레이터가 즉시 수정합니다.

---

### 2.6 실행 모드

#### session-wrap 방식

```
/wrap                    → 전체 워크플로우 (5단계, 사용자 선택)
/wrap "fix auth bug"     → 즉시 커밋 (분석 없이)
```

두 가지 모드만 있습니다.

#### Snapkin 방식

```
/snapkin                 → Full 모드 (4단계 + 자동 커밋)
/snapkin quick           → Quick 모드 (Session Context만 + 빠른 커밋)
/snapkin quick "msg"     → Quick 모드 + 커스텀 메시지
/snapkin review          → Full 모드 + 커밋 전 사용자 확인
```

**Quick 모드 예시**:

```bash
# 30분 작업 후 빠르게 체크포인트
$ /snapkin quick "auth middleware WIP"

# 결과 (10초 내 완료)
## Snapkin Quick Sync Complete

**Date**: 2026-02-05
**Commit**: a3f2b1c
**Mode**: Quick

Session Context 업데이트됨:
- Last Sync: 2026-02-05
- Session: auth middleware WIP
- Active Work: git diff 기반 자동 요약

전체 레슨 추출은 `/snapkin`을 사용하세요.
```

**장점**: 중간 체크포인트용. historian 호출 없이 빠르게 상태만 저장.

---

## Part 3: 적합한 Use Cases

### session-wrap이 적합한 경우

#### 1. 깊은 분석이 필요한 복잡한 세션

```
예시 상황:
- 새로운 아키텍처 도입 (마이크로서비스 전환, 새 프레임워크 적용)
- 대규모 리팩토링
- 여러 팀원과 공유해야 할 결정 사항이 많은 경우

session-wrap 장점:
- 4개 에이전트가 각각의 관점에서 분석
- learning-extractor의 상세한 TIL 형식
- followup-suggester의 프로젝트 관리 수준 태스크
- automation-scout의 구체적인 자동화 제안
```

#### 2. 사용자 통제가 중요한 경우

```
예시 상황:
- 민감한 프로젝트 (금융, 의료)
- 문서 변경에 팀 리뷰가 필요한 경우
- 잘못된 커밋을 방지해야 하는 경우

session-wrap 장점:
- 모든 변경을 사용자가 승인
- 제안을 미리 검토 가능
- 부분 선택 가능 (커밋만, 문서만, 등)
```

#### 3. 자동화 기회를 적극적으로 찾는 경우

```
예시 상황:
- 반복 작업이 많은 프로젝트
- 플러그인/스킬 개발 중
- 개발 생산성 향상이 목표

session-wrap 장점:
- automation-scout의 체계적인 분석
- Skill/Command/Agent 분류
- 구체적인 구현 템플릿
- /plugin-dev:create-plugin 연동
```

#### 4. 프로젝트별 컨텍스트(context.md)를 관리하는 경우

```
예시 상황:
- 여러 프로젝트를 병행
- 각 프로젝트에 고유한 규칙/제약이 있음
- 프로젝트별 히스토리가 중요

session-wrap 장점:
- context.md 지원 (프로젝트별 컨텍스트)
- CLAUDE.md와 context.md 분리
- 프로젝트 컨텍스트 자동 분석
```

---

### Snapkin이 적합한 경우

#### 1. 빠른 일상적 세션 정리

```
예시 상황:
- 매일 퇴근 전 정리
- 버그 수정, 작은 기능 추가
- 빠르게 다음 세션으로 넘어가야 할 때

Snapkin 장점:
- /snapkin quick으로 10초 내 완료
- 자동 커밋으로 추가 작업 없음
- "무엇이 바뀔까?" 고민 없이 실행
```

**Quick 모드 실제 예시**:

```bash
# 18:00 - 퇴근 전
$ /snapkin quick "auth module 90% done"

# 10초 후
✓ Commit: docs: snapkin quick sync (2026-02-05) - auth module 90% done

# 다음 날 09:00
$ claude
> # CLAUDE.md의 Next Entry Point 자동 로드
> [P1] 리프레시 토큰 저장소 연동 — src/auth/token-store.ts:23

# 바로 작업 시작 가능!
```

#### 2. 지식 축적이 중요한 경우

```
예시 상황:
- 새로운 기술/도메인 학습 중
- 팀 온보딩 문서가 필요
- 실수를 반복하지 않으려는 경우

Snapkin 장점:
- LESSONS.md에 자동 축적
- 6개 카테고리로 체계적 분류
- 날짜별 히스토리
- 중복 자동 제거
```

**LESSONS.md 축적 예시**:

```markdown
# 3개월 후의 LESSONS.md

---

## 2026-04-15

- **[Error-Fix]** Prisma 마이그레이션 후 generate 필수 — 스키마 변경 후 `prisma generate` 안 하면 타입 불일치.
- **[Insight]** Next.js 13 app router에서 'use client'는 파일 최상단에만 — 컴포넌트 중간에 넣으면 무시됨.

## 2026-04-10

- **[Decision]** 상태 관리 Zustand 선택 — Redux보다 보일러플레이트 적고, 러닝커브 낮음.
- **[Domain]** 한국 결제 PG는 아임포트 권장 — 국내 카드사 연동이 간편.

## 2026-04-05

- **[Error-Fix]** React useEffect cleanup은 반드시 동기 함수 — async cleanup은 경고 발생.
...

# 수십 개의 레슨이 날짜별로 축적됨
# grep으로 카테고리별 검색 가능: grep "\[Error-Fix\]" LESSONS.md
```

#### 3. 일관된 문서 포맷이 필요한 경우

```
예시 상황:
- 팀에서 CLAUDE.md 포맷을 표준화
- 새 팀원이 프로젝트에 빠르게 적응해야 함
- 자동화된 문서 품질 관리가 필요

Snapkin 장점:
- 고정된 Session Context 구조
- P0-P3 우선순위로 일관된 handoff
- validator의 구조 검증
- 보안 자동 스캔
```

#### 4. 보안이 중요한 경우

```
예시 상황:
- API 키, 비밀번호를 다루는 프로젝트
- 실수로 credential이 문서에 들어갈 위험
- 자동화된 보안 검사가 필요

Snapkin 장점:
- validator의 보안 패턴 스캔
- 발견 시 자동 [REDACTED] 처리
- 커밋 전 항상 검사
```

---

### 복합 사용 사례

두 플러그인을 **함께 사용**할 수도 있습니다:

```
# 일상적 세션 (80%)
/snapkin quick "feature X done"
→ 빠른 체크포인트, 자동 커밋

# 중요한 세션 (15%)
/snapkin
→ Full 모드로 레슨까지 추출

# 심층 분석이 필요한 세션 (5%)
/wrap
→ 자동화 기회 탐색, 상세 태스크 정의
```

---

## Part 4: Snapkin이 정말 필요한가? — 인사이트 도출

### 핵심 질문: session-wrap으로 충분하지 않은가?

session-wrap은 이미 강력한 5개 에이전트를 가지고 있습니다. 그런데 왜 Snapkin을 만들었을까요?

#### 인사이트 1: "분석 피로" 문제

```
session-wrap 사용 패턴:

Day 1: /wrap → 상세 분석 → 꼼꼼히 검토 → 선택 실행 (10분)
Day 2: /wrap → 상세 분석 → 대충 훑어봄 → 전부 선택 (5분)
Day 3: /wrap → 상세 분석 → 그냥 커밋만 (3분)
Day 4: /wrap "quick fix" → 즉시 커밋 (10초)
Day 5~N: /wrap "..." → 계속 즉시 커밋...

결론: 대부분의 세션에서 상세 분석을 읽지 않게 됨
```

**Snapkin의 해답**:
- Quick 모드가 기본 → 10초 내 완료
- Full 모드는 필요할 때만 → 레슨 추출 포함
- Review 모드로 확인 필요할 때만 → 사용자 통제

#### 인사이트 2: "지식 축적" 부재

```
session-wrap의 learning-extractor:
- 매우 상세한 분석 제공
- 하지만 저장은 사용자 몫
- 결과: 대부분 복사-붙여넣기 없이 그냥 넘어감
- 1년 후: "작년에 이거 어떻게 해결했더라?" → 기록 없음

Snapkin의 historian:
- LESSONS.md에 자동 축적
- 간결한 한 줄 형식
- 결과: 신경 쓰지 않아도 기록됨
- 1년 후: grep "[Error-Fix]" LESSONS.md → 모든 버그 해결 기록
```

**Snapkin의 해답**:
- 전용 파일(LESSONS.md)에 자동 저장
- 사용자가 "저장할까?" 고민할 필요 없음
- 시간이 지날수록 가치 증가

#### 인사이트 3: "일관성 vs 유연성" 트레이드오프

```
session-wrap:
- 유연함: CLAUDE.md, context.md, 어디든 업데이트 가능
- 결과: 프로젝트마다 다른 포맷, 구조
- 문제: 새 팀원이 "CLAUDE.md 어디 봐야 해?"

Snapkin:
- 엄격함: CLAUDE.md + LESSONS.md 고정, 포맷 고정
- 결과: 모든 프로젝트 동일한 구조
- 장점: "CLAUDE.md의 Next Entry Point 보면 돼"
```

**Snapkin의 해답**:
- Opinionated 설계 → 선택지를 줄임
- 2개 파일만 관리 → 단순한 멘탈 모델
- 고정 포맷 → 예측 가능한 구조

#### 인사이트 4: "검증 시점"의 차이

```
session-wrap (쓰기 전 검증):
- 제안 생성 → 중복 검사 → 사용자 승인 → 쓰기
- 장점: 잘못된 내용이 파일에 안 들어감
- 단점: 검증 결과를 사용자가 해석해야 함

Snapkin (쓰기 후 검증):
- 에이전트가 직접 쓰기 → 검증 → 문제 시 수정 → 커밋
- 장점: 사용자 개입 없이 자동 수정
- 단점: 일단 쓰고 나중에 고침
```

**Snapkin의 해답**:
- 보안 문제는 자동 수정 ([REDACTED])
- 구조 문제는 자동 수정 (마커 추가)
- 사용자는 결과만 확인

#### 인사이트 5: "80/20 법칙"

```
세션 유형 분포 (추정):
- 일상적 세션 (작은 변경, 버그 수정): 80%
- 중요한 세션 (기능 완료, 결정 사항): 15%
- 복잡한 세션 (아키텍처, 대규모 변경): 5%

session-wrap: 모든 세션에 동일한 무게
→ 80%의 세션에서 과도한 분석

Snapkin: 세션 유형에 맞는 모드
→ Quick(80%) / Full(15%) / Review+session-wrap(5%)
```

---

### 결론: Snapkin이 필요한 경우

| 상황 | 추천 | 이유 |
|------|------|------|
| 혼자 개발, 빠른 정리 선호 | Snapkin | Quick 모드, 자동 커밋 |
| 팀 협업, 리뷰 필수 | session-wrap | 사용자 승인 기반 |
| 지식 축적이 목표 | Snapkin | LESSONS.md 자동 저장 |
| 자동화 기회 탐색 | session-wrap | automation-scout |
| 표준화된 문서 포맷 | Snapkin | 고정된 구조 |
| 유연한 문서 관리 | session-wrap | context.md 지원 |
| 보안 자동 검사 | Snapkin | validator 보안 스캔 |
| 상세한 태스크 정의 | session-wrap | followup-suggester |

**최종 인사이트**:

> Snapkin은 session-wrap의 **대체재가 아니라 보완재**입니다.
>
> - **일상의 80%** → Snapkin (빠름, 자동, 축적)
> - **중요한 15%** → Snapkin Full 또는 Review
> - **복잡한 5%** → session-wrap (깊은 분석)

---

## Part 5: Snapkin 개선 방향

현재 Snapkin v2의 한계와 개선 방향을 정리합니다.

### 5.1 단기 개선 (v2.1)

#### 1. followup-suggester 기능 통합

**현재 문제**: Next Entry Point가 너무 간결함

```markdown
# 현재 (Snapkin)
### Next Entry Point
- **[P1]** 리프레시 토큰 저장소 연동 — `src/auth/token-store.ts:23`

# 목표 (개선)
### Next Entry Point
- **[P1]** 리프레시 토큰 저장소 연동 — `src/auth/token-store.ts:23`
  - Effort: Medium (2-3h)
  - Depends: Redis 설정 완료
  - Done: [ ] 저장 [ ] 조회 [ ] 삭제 [ ] 만료
```

**개선 방안**: auditor에 선택적 상세 모드 추가

```markdown
# /snapkin --detailed
→ Next Entry Point에 Effort, Dependencies, Done Criteria 포함
```

#### 2. 레슨 상세도 옵션

**현재 문제**: 한 줄 레슨이 복잡한 내용을 담기 어려움

```markdown
# 현재 (한 줄)
- **[Error-Fix]** JWT 만료 시간에 숫자 15 대신 문자열 '15m' 사용해야 함.

# 목표 (확장 가능)
- **[Error-Fix]** JWT 만료 시간에 숫자 15 대신 문자열 '15m' 사용해야 함.

  <details>
  <summary>상세</summary>

  **증상**: 로그인 직후 토큰 만료
  **원인**: `expiresIn: 15`는 15초로 해석됨
  **해결**: `expiresIn: '15m'` 문자열 사용

  ```javascript
  // Bad
  jwt.sign(payload, secret, { expiresIn: 15 });

  // Good
  jwt.sign(payload, secret, { expiresIn: '15m' });
  ```
  </details>
```

**개선 방안**: historian에 `<details>` 확장 블록 지원

#### 3. TODO/FIXME 자동 스캔

**현재 문제**: 코드베이스의 TODO를 수동으로 찾아야 함

**개선 방안**: Phase 1에서 자동 스캔

```bash
# Dispatch 단계에서 추가
grep -r "TODO\|FIXME\|HACK\|WIP" --include="*.ts" --include="*.js"
```

스캔 결과를 auditor에게 전달하여 Blockers나 Next Entry Point에 반영

---

### 5.2 중기 개선 (v3.0)

#### 1. 자동화 생성 연동

**현재 문제**: `[Future]` 태그로 기록만 하고 실행으로 연결 안 됨

**개선 방안**: `/snapkin:automate` 명령어 추가

```bash
# LESSONS.md의 [Future] 항목을 스캔
$ /snapkin:automate

Found 3 automation candidates:

1. [Future] 토큰 검증 테스트 헬퍼 (2026-02-05)
   → Recommend: Skill

2. [Future] DB 마이그레이션 자동화 (2026-02-03)
   → Recommend: pre-commit hook

3. [Future] API 응답 형식 생성기 (2026-01-28)
   → Recommend: Command

Which to implement? [1/2/3/skip]
```

선택하면 `/plugin-dev:create-plugin`으로 연결하거나 간단한 것은 직접 생성

#### 2. Multi-Session 분석

**현재 문제**: 각 세션이 독립적으로 분석됨

**개선 방안**: 주간/월간 회고 모드

```bash
$ /snapkin:weekly

## Weekly Retrospective (2026-02-01 ~ 2026-02-07)

### Commits
- 12 snapkin syncs
- 5 quick syncs

### Lessons Learned
- [Error-Fix]: 3개 (JWT, Prisma, React hooks)
- [Decision]: 2개 (Zustand, 아임포트)
- [Future]: 4개 (자동화 후보)

### Recurring Patterns
⚠️ "JWT 관련 에러"가 3회 등장 → 인증 모듈 리팩토링 필요?

### Automation ROI
- "DB 마이그레이션 자동화" 3회 언급
  → 예상 절감: 주당 30분
  → 구현 권장도: HIGH

### Next Week Priorities
1. [P1] 인증 모듈 안정화 (에러 빈도 기준)
2. [P1] DB 마이그레이션 자동화 구현
3. [P2] 테스트 커버리지 향상
```

#### 3. 팀 협업 기능

**현재 문제**: 개인 사용에 최적화, 팀 공유 어려움

**개선 방안**:

```markdown
# LESSONS.md에 작성자 태그 추가
- **[Error-Fix]** @elon JWT 만료 시간 문자열로...

# 팀 레슨 통합 명령어
$ /snapkin:team-sync
→ 팀원들의 LESSONS.md를 병합하여 TEAM-LESSONS.md 생성
```

---

### 5.3 장기 비전 (v4.0)

#### 1. AI 기반 패턴 인식

```
현재: historian이 diff를 보고 레슨 추출
미래: 과거 LESSONS.md를 학습하여 패턴 인식

예시:
- "이 에러는 과거에 3번 발생했고, 매번 같은 원인이었음"
- "이 결정은 2달 전 결정과 모순됨 — 검토 필요"
- "이 코드 패턴은 과거에 [Error-Fix]로 기록된 적 있음 — 주의"
```

#### 2. IDE 통합

```
현재: CLI에서만 사용
미래: VS Code 확장

기능:
- CLAUDE.md Session Context를 사이드바에 표시
- P0 태스크 하이라이트
- Next Entry Point 클릭 시 해당 파일로 이동
- 저장 시 자동 /snapkin quick
```

#### 3. 지식 그래프

```
현재: LESSONS.md는 날짜별 선형 리스트
미래: 연결된 지식 그래프

예시:
JWT 토큰 ← 관련 → 인증 미들웨어
    ↑                    ↑
    └── 관련 에러 ──┘

    ↓
검색: "JWT" → 관련 레슨 5개 + 관련 파일 3개 + 관련 결정 2개
```

---

### 5.4 개선 우선순위 매트릭스

| 개선 항목 | 가치 | 노력 | 우선순위 |
|----------|------|------|----------|
| TODO/FIXME 스캔 | HIGH | LOW | **P1** |
| 레슨 상세 모드 | MEDIUM | LOW | **P1** |
| Next Entry Point 상세화 | MEDIUM | MEDIUM | **P2** |
| 자동화 생성 연동 | HIGH | MEDIUM | **P2** |
| 주간/월간 회고 | HIGH | HIGH | **P2** |
| 팀 협업 기능 | MEDIUM | HIGH | **P3** |
| AI 패턴 인식 | HIGH | VERY HIGH | **P3** |
| IDE 통합 | MEDIUM | VERY HIGH | **P3** |

---

## 마치며: 당신의 선택은?

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   "오늘 뭐 했더라?"를 없애는 두 가지 방법                     │
│                                                             │
│   session-wrap: "다 분석해서 보여줄게. 뭐 할지 골라."        │
│   Snapkin:      "내가 알아서 정리했어. 커밋도 했어."         │
│                                                             │
│   당신의 스타일은?                                          │
│                                                             │
│   [ ] 통제 선호 → session-wrap                              │
│   [ ] 자동화 선호 → Snapkin                                 │
│   [ ] 둘 다 → 상황에 맞게 병행                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

어떤 도구를 선택하든, 중요한 건 **사용하는 것**입니다.

세션 정리 없이 다음 날 15분을 헤매는 것보다, 오늘 30초 투자해서 정리하는 게 낫습니다.

---

## 부록: 빠른 시작 가이드

### session-wrap 설치 및 사용

```bash
# 설치 (Claude Code 플러그인)
claude /plugin install session-wrap

# 사용
/wrap                    # 전체 분석
/wrap "commit message"   # 즉시 커밋
```

### Snapkin 설치 및 사용

```bash
# 설치 (Claude Code 플러그인)
claude /plugin install snapkin

# 초기화 (첫 사용)
/snapkin:snapkin-init

# 사용
/snapkin              # Full 모드 (기본)
/snapkin quick        # Quick 모드 (빠른 체크포인트)
/snapkin quick "msg"  # Quick + 커스텀 메시지
/snapkin review       # Full + 커밋 전 확인
```

### 병행 사용 추천 패턴

```bash
# 일상 (매일)
/snapkin quick "done for today"

# 주요 기능 완료 시 (주 2-3회)
/snapkin

# 복잡한 세션 종료 시 (월 1-2회)
/wrap
```

---

*이 문서는 Snapkin v2.0과 session-wrap v1.0 기준으로 작성되었습니다.*
*최신 버전에서는 기능이 변경되었을 수 있습니다.*
