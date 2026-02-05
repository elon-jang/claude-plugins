# Snapkin vs session-wrap 비교 분석

두 플러그인 모두 세션 종료 시 작업 내용을 정리하는 목적을 가지지만, 철학과 구현 방식이 다릅니다.

## 한눈에 비교

| 항목 | **Snapkin v2** | **session-wrap** |
|------|----------------|------------------|
| **에이전트 수** | 3개 (historian, auditor, validator) | 5개 (doc-updater, automation-scout, learning-extractor, followup-suggester, duplicate-checker) |
| **대상 파일** | 2개 (CLAUDE.md, LESSONS.md) | 2개+ (CLAUDE.md, context.md, 기타) |
| **파일 소유권** | 엄격 (1 에이전트 = 1 파일) | 없음 (제안만 함) |
| **파일 쓰기** | 직접 쓰기 | 제안만 (사용자가 실행) |
| **커밋** | 자동 커밋 | 사용자 선택 |
| **워크플로우** | 4단계 고정 | 5단계 (사용자 선택 포함) |
| **Quick 모드** | O | O (인자로 커밋 메시지) |
| **Review 모드** | O | 기본 동작 |

---

## 아키텍처 비교

### Snapkin v2

```
┌─────────────────────────────────────────────────────────┐
│  Mode Selection                                         │
│  /snapkin | /snapkin quick | /snapkin review            │
├─────────────────────────────────────────────────────────┤
│  Phase 1: Dispatch                                      │
│  git diff + docs 읽기 + session summary                 │
├─────────────────────────────────────────────────────────┤
│  Phase 2: Parallel Scribble                             │
│  ┌───────────┐  ┌───────────┐                           │
│  │ historian │  │  auditor  │  ← 직접 파일 쓰기         │
│  │LESSONS.md │  │ CLAUDE.md │                           │
│  └───────────┘  └───────────┘                           │
├─────────────────────────────────────────────────────────┤
│  Phase 3: Validate                                      │
│  ┌───────────────────────────┐                          │
│  │ validator (read-only)     │  ← 보안/구조/중복 검사   │
│  └───────────────────────────┘                          │
├─────────────────────────────────────────────────────────┤
│  Phase 3.5: User Review (review 모드만)                 │
├─────────────────────────────────────────────────────────┤
│  Phase 4: Snap-Commit                                   │
│  git add + commit (자동)                                │
└─────────────────────────────────────────────────────────┘
```

### session-wrap

```
┌─────────────────────────────────────────────────────────┐
│  /wrap 또는 /wrap [commit message]                      │
├─────────────────────────────────────────────────────────┤
│  Step 1: Check Git Status                               │
├─────────────────────────────────────────────────────────┤
│  Step 2: Phase 1 (4 Agents in Parallel)                 │
│  ┌─────────────┬─────────────┐                          │
│  │ doc-updater │ automation- │                          │
│  │             │ scout       │                          │
│  ├─────────────┼─────────────┤  ← 분석 + 제안           │
│  │ learning-   │ followup-   │                          │
│  │ extractor   │ suggester   │                          │
│  └─────────────┴─────────────┘                          │
├─────────────────────────────────────────────────────────┤
│  Step 3: Phase 2 (Sequential)                           │
│  ┌───────────────────────────┐                          │
│  │   duplicate-checker       │  ← 중복 검증             │
│  └───────────────────────────┘                          │
├─────────────────────────────────────────────────────────┤
│  Step 4: Integrate Results & Present                    │
├─────────────────────────────────────────────────────────┤
│  Step 5: User Selection (AskUserQuestion)               │
│  커밋 / CLAUDE.md 업데이트 / 자동화 생성 / 건너뛰기     │
├─────────────────────────────────────────────────────────┤
│  Step 6: Execute Selected Actions                       │
└─────────────────────────────────────────────────────────┘
```

---

## 철학적 차이

### Snapkin: "Opinionated Automation"

- **핵심 가치**: 빠르고 일관된 세션 정리
- **접근법**: 에이전트가 직접 파일을 쓰고 커밋까지 자동 완료
- **가정**: 대부분의 세션 정리는 정형화 가능
- **사용자 역할**: 결과 확인 (review 모드로 선택적 개입)

### session-wrap: "Advisory Analysis"

- **핵심 가치**: 포괄적 분석과 유연한 선택
- **접근법**: 에이전트가 분석/제안만 하고, 사용자가 실행
- **가정**: 각 세션은 다양한 후속 작업이 필요할 수 있음
- **사용자 역할**: 제안 검토 후 선택적 실행

---

## 기능별 상세 비교

### 1. 문서 업데이트

| 측면 | Snapkin | session-wrap |
|------|---------|--------------|
| **방식** | auditor가 직접 CLAUDE.md 수정 | doc-updater가 제안, 사용자가 적용 |
| **컨벤션 관리** | CLAUDE.md 상단부 자동 업데이트 | 제안만 제공 |
| **세션 컨텍스트** | 전용 마커 사이 섹션 완전 재작성 | context.md에 추가 제안 |
| **우선순위** | P0-P3 태그로 Next Entry Point | 없음 |

**Snapkin 장점**: 일관된 포맷, 자동 업데이트, 세션 간 연속성
**session-wrap 장점**: 유연성, 사용자 통제, 여러 context.md 지원

### 2. 레슨/학습 추출

| 측면 | Snapkin | session-wrap |
|------|---------|--------------|
| **파일** | LESSONS.md (전용) | 별도 파일 없음 (TIL 형식 제안) |
| **방식** | historian이 직접 작성 | learning-extractor가 분석만 |
| **카테고리** | 6개 태그 (`[Error-Fix]`, `[Decision]`, `[Insight]`, `[Domain]`, `[Prompt]`, `[Future]`) | 5개 카테고리 (Technical, Problem-Solving, Domain, Process, Mistakes) |
| **중복 체크** | historian 내장 + validator | duplicate-checker |
| **자동화 후보** | historian의 `[Future]` 태그 | automation-scout (전용 에이전트) |

**Snapkin 장점**: 전용 파일로 지식 축적, 날짜별 자동 정리
**session-wrap 장점**: 상세한 분석 프레임워크, 별도 자동화 전문 에이전트

### 3. 자동화 발견

| 측면 | Snapkin | session-wrap |
|------|---------|--------------|
| **전담 에이전트** | 없음 (historian이 `[Future]`로 기록) | automation-scout (전용) |
| **분류** | 단순 기록 | Skill/Command/Agent 분류 |
| **구현 가이드** | 없음 | 상세한 구현 템플릿 제공 |
| **plugin-dev 연동** | 없음 | 있음 (`/plugin-dev:create-plugin`) |

**Snapkin 장점**: 단순함, 오버헤드 없음
**session-wrap 장점**: 체계적 자동화 분석, 즉시 구현 가능한 템플릿

### 4. 후속 작업 관리

| 측면 | Snapkin | session-wrap |
|------|---------|--------------|
| **전담 에이전트** | 없음 | followup-suggester (전용) |
| **우선순위 시스템** | P0-P3 (Next Entry Point에만) | P0-P3 (전체 태스크에) |
| **TODO 스캔** | 없음 | Grep으로 TODO/FIXME/WIP 검색 |
| **태스크 상세도** | 간략 (1-5 항목) | 상세 (Done Criteria, Dependencies, Effort 포함) |

**Snapkin 장점**: 간결함, 핵심만 기록
**session-wrap 장점**: 체계적 태스크 관리, 프로젝트 관리 수준

### 5. 검증

| 측면 | Snapkin | session-wrap |
|------|---------|--------------|
| **에이전트** | validator (read-only, haiku) | duplicate-checker (haiku) |
| **검사 범위** | 보안 + 구조 + 중복 + 사이즈 | 중복만 |
| **보안 스캔** | API 키, 비밀번호, 토큰 패턴 | 없음 |
| **구조 검증** | Session Context 마커, 필수 섹션 | 없음 |

**Snapkin 장점**: 포괄적 검증, 보안 자동 체크
**session-wrap 장점**: 중복에 집중, 가벼움

### 6. 커밋

| 측면 | Snapkin | session-wrap |
|------|---------|--------------|
| **기본 동작** | 자동 커밋 | 사용자 선택 |
| **커밋 메시지** | 정형화 (`docs: snapkin session sync (날짜) - 요약`) | 사용자 제공 또는 선택 |
| **베이스라인** | 마지막 sync 커밋부터 diff | HEAD~3 |

**Snapkin 장점**: 일관된 커밋 히스토리, 완전 자동화
**session-wrap 장점**: 유연한 커밋 전략

---

## 모드 비교

### Snapkin 모드

| 모드 | 명령어 | 동작 |
|------|--------|------|
| **Full** | `/snapkin` | 4단계 전체 실행 + 자동 커밋 |
| **Quick** | `/snapkin quick [msg]` | Session Context만 업데이트 + 빠른 커밋 |
| **Review** | `/snapkin review` | 4단계 + 커밋 전 사용자 확인 |

### session-wrap 모드

| 모드 | 명령어 | 동작 |
|------|--------|------|
| **Interactive** | `/wrap` | 5단계 전체 + 사용자 선택 |
| **Quick Commit** | `/wrap [message]` | 즉시 커밋 |

---

## 언제 무엇을 사용할까?

### Snapkin 추천 상황

1. **빠른 세션 정리가 필요할 때** - Quick 모드로 30초 내 완료
2. **일관된 문서 포맷을 원할 때** - Session Context 구조 고정
3. **지식 축적이 중요할 때** - LESSONS.md에 체계적 기록
4. **자동화를 선호할 때** - 별도 선택 없이 커밋까지 완료
5. **P0-P3 우선순위가 필요할 때** - Next Entry Point 명확화

### session-wrap 추천 상황

1. **상세한 분석이 필요할 때** - 4개 에이전트의 다각도 분석
2. **자동화 기회를 찾을 때** - automation-scout의 체계적 분석
3. **유연한 후속 작업을 원할 때** - followup-suggester의 상세 태스크
4. **선택적 실행을 원할 때** - 제안 중 필요한 것만 선택
5. **context.md를 사용할 때** - 프로젝트별 컨텍스트 관리

---

## 통합 가능성

두 플러그인의 장점을 결합하는 방법:

### 이미 Snapkin v2에 반영된 것

| session-wrap 기능 | Snapkin v2 통합 방식 |
|-------------------|---------------------|
| P0-P3 우선순위 | Next Entry Point에 적용 |
| Quick 모드 | `/snapkin quick` |
| Review 모드 | `/snapkin review` |
| 자동화 감지 | historian의 `[Future]` 태그 + Automation Candidate Detection |
| 학습 추출 강화 | historian의 Deep Extraction 가이드 |
| Validator | 별도 에이전트로 Phase 3 담당 |

### 향후 통합 고려사항

| session-wrap 기능 | 통합 가치 | 난이도 |
|-------------------|-----------|--------|
| followup-suggester | MEDIUM - Next Entry Point 강화 | LOW |
| TODO/FIXME 스캔 | LOW - 이미 git diff로 커버 | LOW |
| context.md 지원 | LOW - CLAUDE.md로 충분 | MEDIUM |
| plugin-dev 연동 | MEDIUM - 자동화 구현 지원 | HIGH |

---

## 결론

| 관점 | 승자 | 이유 |
|------|------|------|
| **속도** | Snapkin | Quick 모드, 자동 커밋 |
| **단순성** | Snapkin | 2 파일, 3 에이전트, 고정 워크플로우 |
| **분석 깊이** | session-wrap | 5개 전문 에이전트 |
| **유연성** | session-wrap | 사용자 선택 기반 |
| **자동화 발견** | session-wrap | 전용 에이전트 + 구현 템플릿 |
| **지식 축적** | Snapkin | LESSONS.md 전용 파일 |
| **보안** | Snapkin | validator의 보안 스캔 |
| **일관성** | Snapkin | 정형화된 포맷과 커밋 |

**최종 권장**:
- 일상적 세션 정리 → **Snapkin** (빠르고 일관됨)
- 깊은 분석이 필요한 세션 → **session-wrap** (상세하고 유연함)
- 두 플러그인 병행 사용 가능 (목적에 따라 선택)
