# Project Specification: Shortcut Master

## Overview

애플리케이션 단축키를 GitHub에 저장하고, 효과적으로 학습하고 검색할 수 있는 개인 단축키 관리 시스템입니다. Leitner Box 기반의 간단하고 효과적인 학습 알고리즘을 제공합니다.

## Target Users

- **주요 대상**: 단축키 암기가 필요한 개발자 및 생산성 도구 사용자
- **워크플로우**: 단축키 등록 → 키워드 검색 → 학습 모드로 반복 연습
- **기대 효과**: 자주 틀리는 단축키를 집중 복습하여 빠른 암기

## Technology Stack

| 구성 요소       | 기술                      | 비고                    |
| -------------- | ------------------------- | ----------------------- |
| Language       | Python 3.12+              |                         |
| Storage Format | Markdown (Table)          | 사람이 읽기 쉬운 형식    |
| Learning Data  | JSON                      | `.shortcut-master/` 폴더 |
| Search         | Regex + Fuzzy Matching    | 제목/설명/카테고리 검색  |
| Learning System| Leitner Box (3-box)       | 간단하고 효과적          |
| Git Integration| GitPython                 | 자동 commit              |
| Table Formatting| tabulate                 | Markdown 테이블 정렬     |

## Architecture

### Data Structure

```
shortcuts-repo/                    # 사용자가 지정하는 저장소
├── vscode_shortcuts.md            # VS Code 단축키 목록
├── gmail_shortcuts.md             # Gmail 단축키 목록
├── chrome_shortcuts.md            # Chrome 단축키 목록
├── .shortcut-master/
│   ├── config.json                # 저장소 설정
│   └── learning-progress.json     # 학습 진도 (로컬 전용)
├── .gitignore                     # learning-progress.json 제외
└── README.md
```

### Markdown Format (vscode_shortcuts.md)

```markdown
# VS Code Shortcuts

## Editing

| Shortcut | Description | Category |
|----------|-------------|----------|
| Cmd+D | Select next occurrence | Selection |
| Cmd+Shift+L | Select all occurrences | Selection |
| Cmd+/ | Toggle line comment | Comment |

## Navigation

| Shortcut | Description | Category |
|----------|-------------|----------|
| Cmd+P | Quick Open | Files |
| Cmd+Shift+O | Go to Symbol | Navigation |
```

**필수 요소**:
- `Shortcut`: 단축키 조합 (엄격한 형식: `Cmd+Shift+P`)
- `Description`: 기능 설명 (검색 대상)
- `Category`: 분류 (자동완성 제공)
- `## Section`: 섹션 헤더 (기능적 의미 - 필터링 가능)

**단축키 표기법 규칙**:
- Modifier Keys: `Cmd`, `Shift`, `Ctrl`, `Alt` (첫 글자 대문자)
- 일반 키: 대문자 (`P`, `D`, `/`)
- 구분자: `+` (공백 없음)
- 예시: `Cmd+Shift+P`, `Ctrl+Alt+Delete`
- `/shortcut:shortcut-add` 시 자동으로 표준화

### Learning Progress Format (JSON)

```json
{
  "vscode:Cmd+D": {
    "box": 1,
    "lastReviewed": "2026-01-15T10:30:00",
    "correctCount": 3,
    "incorrectCount": 1,
    "addedDate": "2026-01-10T08:00:00"
  },
  "gmail:Cmd+Shift+C": {
    "box": 2,
    "lastReviewed": "2026-01-14T15:20:00",
    "correctCount": 5,
    "incorrectCount": 0,
    "addedDate": "2026-01-10T08:00:00"
  }
}
```

**필드 설명**:
- `box`: 현재 박스 번호 (1, 2, 3)
- `lastReviewed`: 마지막 복습 시간 (ISO 8601 형식)
- `correctCount`: 누적 정답 횟수
- `incorrectCount`: 누적 오답 횟수
- `addedDate`: 학습 시작 일시

### Leitner Box System (3-Box)

```
Box 1 (자주 복습)     Box 2 (보통)        Box 3 (드물게 복습)
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ 새로운 카드  │      │ 1번 맞힌 것  │      │ 2번 맞힌 것  │
│ 틀린 카드    │  →   │             │  →   │             │
└─────────────┘      └─────────────┘      └─────────────┘
    ↑                     ↑                     ↑
    └─────────틀리면──────┴──────────────────────┘
```

**학습 규칙**:
1. 새 단축키는 Box 1에서 시작
2. 정답 시: 다음 박스로 이동 (Box 3에서는 유지)
3. 오답 시: Box 1으로 이동 (단계적 승급만 허용, 점프 불허)
4. 복습 빈도:
   - Box 1: 매일 (lastReviewed + 1일)
   - Box 2: 3일마다 (lastReviewed + 3일)
   - Box 3: 7일마다 (lastReviewed + 7일)

**복습 타이밍 정책**:
- 정확한 날짜 매칭: `today >= lastReviewed + interval`
- 예: Box 2 카드가 2026-01-15에 복습됨 → 다음 복습일은 2026-01-18
- 2026-01-19에 학습 세션 시작 시: 해당 카드는 표시되지 않음 (이미 지난 복습일은 다음 주기로 대기)

### Module Responsibilities

1. **Repository Manager** (`scripts/repo_manager.py`)
   - 저장소 초기화 (새 저장소 또는 기존 저장소 지정)
   - `.shortcut-master/` 폴더 생성
   - `.gitignore` 설정 (learning-progress.json 제외)
   - 앱 이름 변경 기능 (`/shortcut:shortcut-rename`)

2. **Shortcut Parser** (`scripts/parser.py`)
   - Markdown 테이블 파싱 (캐싱 없음 - 매번 파싱)
   - 단축키 데이터 추출 및 검증
   - 엄격한 형식 검증 (에러 시 중단, 파일명과 라인 번호 표시)
   - 전체 앱의 단축키 목록 로드
   - 섹션(## Header) 파싱 및 필터링 지원
   - 단축키 표기법 정규화 (`Cmd+Shift+P` 형식 강제)

3. **Search Engine** (`scripts/search.py`)
   - 키워드 검색 (앱명, 설명, 카테고리, 섹션)
   - Fuzzy matching (오타 허용)
   - 검색 결과 하이라이팅
   - 앱별 그룹핑 표시
   - 섹션별 필터링 (`--section` 옵션)

4. **Learning System** (`scripts/learning.py`)
   - Leitner Box 알고리즘 구현
   - 복습할 카드 선택 (정확한 날짜 매칭)
   - 정답/오답 처리 및 박스 이동 (단계적 승급만)
   - 학습 통계 생성
   - 3가지 학습 모드 지원:
     - Flash: 플래시카드 (Enter → y/n → Enter)
     - Quick: 난이도 평가 (Enter → 1/2, 점프 불허)
     - Typing: 실제 단축키 입력 감지 (동시 누름만 지원)
   - 세션 단위 저장 (완료 시에만 learning-progress.json 업데이트)

5. **Data Integrity Manager** (`scripts/integrity.py`)
   - 파일과 학습 진도 데이터 정합성 검증
   - 없는 단축키의 학습 진도 자동 삭제
   - 중복 단축키 감지 및 거부

6. **CLI Interface** (`scripts/cli.py`)
   - `/shortcut` 명령 처리
   - 대화형 학습 모드
   - 검색 결과 표시
   - 키보드 입력 최소화 설계
   - 카테고리 자동완성 제공

7. **Formatter** (`scripts/formatter.py`)
   - Markdown 테이블 자동 정렬
   - 커밋 전 포맷팅 수정
   - 일관된 형식 유지

## CLI Commands

### 전체 명령어 목록

```bash
# 저장소 초기화
/shortcut:shortcut-init [repo_path]

# 단축키 추가 (대화형, 카테고리 자동완성 제공)
/shortcut:shortcut-add

# 단축키 삭제 (파일과 학습 진도 모두 제거)
/shortcut:shortcut-delete <app_name> <shortcut>

# 앱 이름 변경 (파일명과 학습 진도 데이터 일괄 변경)
/shortcut:shortcut-rename <old_app_name> <new_app_name>

# 검색
/shortcut:shortcut-search <keyword> [--section=<section_name>]

# 학습 모드 시작
/shortcut:shortcut-learn [app_name] [--mode=flash|quick|typing] [--all]

# 통계 보기
/shortcut:shortcut-stats [app_name]

# 앱 목록 보기
/shortcut:shortcut-list

# Cheat Sheet 생성
/shortcut:shortcut-cheatsheet [output_path] [--mode=simple|progress|interactive]
```

### 명령어 상세 설명

#### `/shortcut:shortcut-init [repo_path]`

저장소 초기화. 새 디렉토리 생성 또는 기존 디렉토리 지정.

```bash
/shortcut:shortcut-init ~/shortcuts

# Creates:
# ~/shortcuts/.shortcut-master/config.json
# ~/shortcuts/.shortcut-master/learning-progress.json
# ~/shortcuts/.gitignore
# ~/shortcuts/README.md
# Initializes git repo
```

#### `/shortcut:shortcut-add`

대화형 단축키 추가. 자동완성 및 표기법 정규화 제공.

```
App: vscode (autocomplete from existing apps)
Category: Editing (autocomplete from existing categories)
Shortcut: cmd+d (자동으로 Cmd+D로 변환)
Description: Select next occurrence

✓ Added to vscode_shortcuts.md
✓ Committed: Add shortcut: Cmd+D
```

**중복 감지**: 동일한 단축키가 이미 존재하면 에러 표시 후 거부.

#### `/shortcut:shortcut-delete <app> <shortcut>`

단축키 삭제. 파일과 학습 진도 모두 제거.

```bash
/shortcut:shortcut-delete vscode "Cmd+D"

# Removes from vscode_shortcuts.md
# Removes from learning-progress.json
# Auto-commits: Delete shortcut: Cmd+D
```

#### `/shortcut:shortcut-rename <old> <new>`

앱 이름 변경. 파일명과 학습 진도 키를 일괄 변경.

```bash
/shortcut:shortcut-rename vscode vscode-insiders

# Renames: vscode_shortcuts.md → vscode-insiders_shortcuts.md
# Updates all keys in learning-progress.json
# Auto-commits: Rename app: vscode → vscode-insiders
```

#### `/shortcut:shortcut-search <keyword>`

키워드 검색. 앱별 그룹핑 표시.

```bash
/shortcut:shortcut-search "comment"

=== Search Results for "comment" ===

[VS Code]
  Cmd+/         Toggle line comment        (Editing)
  Cmd+K Cmd+C   Add line comment          (Editing)

[Gmail]
  Cmd+/         Search emails             (Navigation)

Found 3 shortcuts across 2 apps.
```

**섹션 필터링**:
```bash
/shortcut:shortcut-search "toggle" --section=Editing

# Only searches within ## Editing sections
```

#### `/shortcut:shortcut-learn [app] [--mode] [--all]`

학습 모드 시작.

```bash
# Flash Mode (기본) - 오늘 복습할 카드만
/shortcut:shortcut-learn vscode

# Quick Mode
/shortcut:shortcut-learn vscode --mode=quick

# Typing Mode (동시 누름만 지원)
/shortcut:shortcut-learn vscode --mode=typing

# 강제로 모든 카드 복습
/shortcut:shortcut-learn vscode --all
```

**복습 카드 선택 로직**:
1. `--all` 없으면: 오늘 복습 예정 카드만 (`today >= lastReviewed + interval`)
2. `--all` 있으면: 모든 카드
3. 카드가 없으면: "오늘 복습할 카드가 없습니다. 다음 복습: 2026-01-18" 표시 후 종료

**문제 수 부족 시**:
- quizSize=10인데 카드가 7개면: 7개만 출제
- "오늘은 7문제로 진행합니다" 안내

#### `/shortcut:shortcut-stats [app]`

학습 통계 표시.

```bash
/shortcut:shortcut-stats vscode

=== Learning Statistics: VS Code ===

Box Distribution:
  Box 1: 5 cards (review now)
  Box 2: 12 cards (next: 2026-01-18)
  Box 3: 23 cards (next: 2026-01-22)

Overall Accuracy: 85.3%
  Correct: 142 / Incorrect: 24

Recent Activity (Last 7 days):
  Sessions: 5
  Questions answered: 47

Most Difficult Shortcuts (Top 5):
  1. Cmd+K Cmd+S - incorrectCount: 8
  2. Cmd+Shift+F - incorrectCount: 5
  3. Cmd+P - incorrectCount: 4
  ...
```

#### `/shortcut:shortcut-cheatsheet [output] [--mode]`

A4 인쇄용 Cheat Sheet HTML 생성.

```bash
# 기본 (체크박스 없음)
/shortcut:shortcut-cheatsheet

# 학습 진행상황 표시
/shortcut:shortcut-cheatsheet --mode=progress

# 직접 체크 가능 (브라우저용)
/shortcut:shortcut-cheatsheet ~/Desktop/shortcuts.html --mode=interactive
```

**체크박스 모드:**

| 모드 | 설명 | 용도 |
|------|------|------|
| `simple` | 체크박스 없음 (기본값) | 인쇄용 |
| `progress` | 학습 진행상황 기반 (읽기 전용) | 학습 현황 확인 |
| `interactive` | 브라우저에서 직접 체크 | 수동 체크리스트 |

**Progress 모드 체크박스:**
- ✓ = Box 3 (마스터)
- △ = Box 2 (진행 중)
- □ = Box 1 또는 미학습

**Interactive 모드:**
- 브라우저에서 체크박스 클릭 가능
- `localStorage`에 자동 저장 (브라우저 종료 후에도 유지)
- 실시간 진행률 표시

## Input/Output Specifications

### Flash Mode (기본)

```
=== Learning Mode: VS Code (Flash) ===
Box 1: 5 cards | Box 2: 3 cards | Box 3: 2 cards

[Question 1/10] Box 1
What does this shortcut do?

  Cmd+D

[Press Enter to reveal answer]
```

```
=== Answer ===

  Cmd+D

  → Select next occurrence

  Category: Editing
  Section: Editing

Did you remember correctly?
  [y] Yes - move to Box 2
  [n] No - stay in Box 1
  [s] Skip
```

### Quick Mode

```
=== Answer ===

  Cmd+D → Select next occurrence

How well did you know it?
  [1] Didn't know - stay in Box 1
  [2] Got it - move to Box 2

(Quick Mode에서는 점프 불허)
```

### Typing Mode

동시 누름만 지원 (`Cmd+Shift+P`). 멀티 키 시퀀스(`Cmd+K → Cmd+S`)는 Flash/Quick Mode 사용 권장.

```
[Question 1/10] Box 1

What is the shortcut for:
"Toggle line comment"

[Press the actual shortcut combination]

✓ Correct! You pressed Cmd+/
[Box 1 → Box 2]

[Press Enter to continue...]
```

### 학습 세션 완료

```
=== Learning Session Complete ===

Today's Progress:
  Correct: 8/10 (80%)
  Incorrect: 2/10 (20%)

Box Changes:
  Box 1 → Box 2: 5 shortcuts ↑
  Box 2 → Box 3: 2 shortcuts ↑
  Box 3 → Box 1: 1 shortcut ↓
  Stayed in Box 1: 2 shortcuts

Progress:
  Box 1: 4 shortcuts (review tomorrow)
  Box 2: 7 shortcuts (next review: Jan 18)
  Box 3: 5 shortcuts (next review: Jan 22)

Total mastery: 75% (Box 2+3)
```

## Error Handling

### 저장소 오류

| 오류 유형   | 메시지                                    |
| ----------- | ----------------------------------------- |
| 미초기화    | "저장소가 초기화되지 않았습니다. /shortcut:shortcut-init을 먼저 실행하세요." |
| 경로 없음   | "지정한 경로가 존재하지 않습니다."         |
| Git 오류    | "Git 저장소 초기화 실패. Git이 설치되어 있는지 확인하세요." |

### 파싱 오류 (엄격 검증)

| 오류 유형   | 메시지                                    |
| ----------- | ----------------------------------------- |
| 잘못된 형식 | "vscode_shortcuts.md:15 - 테이블 형식 오류. 필수 컬럼: Shortcut, Description, Category" |
| 빈 파일     | "vscode_shortcuts.md 파일이 비어 있습니다." |
| 파싱 실패   | "vscode_shortcuts.md:23 - 파이프(\|) 누락" |

### 데이터 정합성

| 상황   | 처리                                    |
| ------ | --------------------------------------- |
| 파일에서 단축키 삭제 | 학습 진도 자동 삭제 (조용히 처리) |
| 단축키 중복 추가 | "이미 존재하는 단축키입니다" 에러 후 거부 |
| 앱 이름 불일치 | learning-progress.json에서 해당 앱 키 제거 |

### 학습 모드 오류

| 오류 유형   | 메시지                                    |
| ----------- | ----------------------------------------- |
| 카드 없음   | "학습할 단축키가 없습니다. /shortcut:shortcut-add로 추가하세요." |
| 복습 없음   | "오늘 복습할 카드가 없습니다. 다음 복습: 2026-01-18" |
| 중단 복구   | 세션 단위 저장으로 인해 Ctrl+C 시 진행 내용 손실 |

## Constraints & Limitations

### 의도적 제한

- **플랫폼**: macOS/Linux (Windows는 테스트 환경 부족으로 제외, WSL 권장)
- **저장소**: 로컬 Git 저장소 (GitHub 동기화는 수동 push)
- **학습 진도**: 로컬 전용 (기기 간 동기화 불가)
- **동시 사용**: 단일 사용자 전용
- **학습 모드**: CLI 대화형만 (GUI 없음)
- **검색**: 로컬 검색만 (캐싱 없음 - 매번 파싱)
- **키 입력**: Typing Mode는 동시 누름만 지원 (시퀀스 불가)
- **박스 이동**: 단계적 승급만 (점프 불허)
- **세션 저장**: 완료 시에만 저장 (중단 시 진행 내용 손실)

### 기술적 제한

- Markdown 테이블 형식 엄격 준수 필요
- 단축키 표기법 강제: `Cmd+Shift+P` 형식
- 복습 타이밍: 정확한 날짜 매칭 (늦은 복습은 다음 주기로 대기)
- Git 커밋 메시지: 간단한 형식 (`Add shortcut: Cmd+D`)

## Dependencies

### Python Packages

```
gitpython        # Git 자동화
tabulate         # 테이블 포맷팅 및 정렬
fuzzywuzzy       # Fuzzy search
python-Levenshtein  # Fuzzy matching 성능 개선
rich             # CLI 컬러/포맷팅
pynput           # 키보드 입력 감지 (Typing Mode)
```

### System Dependencies

```bash
# Git 필수
git --version

# macOS/Linux
# Windows는 WSL 권장
```

## Configuration

### Repository Config (`.shortcut-master/config.json`)

```json
{
  "version": "1.0.0",
  "apps": ["vscode", "gmail", "chrome"],
  "settings": {
    "boxIntervals": {
      "box1": 1,
      "box2": 3,
      "box3": 7
    },
    "quizSize": 10,
    "defaultLearningMode": "flash"
  }
}
```

### User Preferences

**복습 간격 커스터마이즈**:
- Box 1: 1일 (기본)
- Box 2: 3일 (기본)
- Box 3: 7일 (기본)

**학습 모드 선택**:
- `flash`: 플래시카드 (기본) - Enter → y/n → Enter
- `quick`: 빠른 학습 - Enter → 1/2
- `typing`: 실제 입력 - 단축키 직접 입력 (동시 누름만)

## Implementation Details

### 단축키 표기법 정규화

`/shortcut:shortcut-add` 입력 시 자동 변환:
- `cmd+d` → `Cmd+D`
- `command+shift+p` → `Cmd+Shift+P`
- `ctrl+alt+delete` → `Ctrl+Alt+Delete`

### 카테고리 자동완성

기존 카테고리 목록 스캔하여 제공:
```
Category (existing: Editing, Navigation, Selection):
> Ed[TAB]
> Editing
```

### Markdown 자동 포맷팅

커밋 전 tabulate로 테이블 정렬:
```python
from tabulate import tabulate

# Before:
| Cmd+D | Select next | Selection |

# After:
| Cmd+D | Select next occurrence | Selection |
```

### 데이터 정합성 자동 정리

학습 시작 시:
1. 모든 `{app}_shortcuts.md` 파일 파싱
2. learning-progress.json의 키와 비교
3. 파일에 없는 키는 조용히 삭제

### Git 커밋 자동화

```python
# Add
git add vscode_shortcuts.md
git commit -m "Add shortcut: Cmd+D"

# Delete
git add vscode_shortcuts.md
git commit -m "Delete shortcut: Cmd+D"

# Rename app
git mv vscode_shortcuts.md vscode-insiders_shortcuts.md
git commit -m "Rename app: vscode → vscode-insiders"
```

## File Structure

```
shortcut-master/                    # 플러그인 디렉토리
├── .claude-plugin/
│   └── plugin.json                 # Claude 플러그인 메타데이터
├── commands/
│   └── shortcut.md                 # /shortcut 명령 정의
├── skills/
│   └── shortcut-master/
│       └── SKILL.md                # Claude 스킬 정의
├── scripts/
│   ├── cli.py                      # CLI 진입점
│   ├── repo_manager.py             # 저장소 관리
│   ├── parser.py                   # Markdown 파싱
│   ├── search.py                   # 검색 엔진
│   ├── learning.py                 # Leitner Box 알고리즘
│   ├── integrity.py                # 데이터 정합성
│   ├── formatter.py                # Markdown 포맷팅
│   └── utils.py                    # 유틸리티
├── templates/
│   ├── shortcuts_template.md       # 새 앱 추가 시 템플릿
│   └── README_template.md          # 저장소 README 템플릿
├── tests/                          # 단위 테스트
│   ├── test_parser.py
│   ├── test_learning.py
│   ├── test_integrity.py
│   └── fixtures/
│       └── sample_vscode_shortcuts.md
├── README.md                       # 사용자 가이드
├── SPEC.md                         # 이 문서
├── CLAUDE.md                       # Claude Code 개발 가이드
└── requirements.txt                # Python 의존성

# 사용자 저장소 예시
~/shortcuts/                        # 사용자가 지정하는 경로
├── .git/
├── .gitignore                      # learning-progress.json 포함
├── .shortcut-master/
│   ├── config.json                 # 저장소 설정
│   └── learning-progress.json      # 학습 진도 (로컬 전용)
├── vscode_shortcuts.md
├── gmail_shortcuts.md
├── chrome_shortcuts.md
└── README.md
```

## Success Metrics

- **사용성**: 단축키 추가/검색이 3번 이내 키 입력으로 완료
- **학습 효율**: Flash Mode 기준 문제당 평균 3번 키 입력 (Enter → y/n → Enter)
- **학습 효과**: 2주 사용 후 Box 3 비율 50% 이상
- **검색 정확도**: Fuzzy matching으로 오타 2글자까지 허용
- **성능**: 1000개 단축키 기준 검색 응답 1초 이내 (캐싱 없이도 달성 가능)
- **데이터 정합성**: 파일 수정 시 자동 정리로 불일치 방지

## Future Plans

> 향후 개선 예정 (현재 버전에서는 제외)

- 이미지 기반 단축키 학습 (스크린샷 첨부)
- 단축키 충돌 감지 (같은 앱 내 중복 경고)
- 학습 진도 시각화 (그래프)
- 멀티 키 시퀀스 지원 (Cmd+K → Cmd+S)
- 웹 대시보드 (선택적)
- Windows 네이티브 지원 (현재는 WSL 권장)
- 기기 간 학습 진도 동기화
