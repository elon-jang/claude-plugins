# Shortcut Master

애플리케이션 단축키를 GitHub에 저장하고, Leitner Box 시스템으로 효과적으로 학습할 수 있는 개인 단축키 관리 플러그인입니다.

## 설치

```bash
/plugin marketplace add elon-jang/claude-plugins
/plugin install shortcut@ai-plugins
```

### 수동 설치

```bash
git clone https://github.com/elon-jang/claude-plugins.git
cd claude-plugins/plugins/shortcut
pip install -r requirements.txt
```

## 사용법

### 명령어

```
/shortcut:shortcut-init [repo_path]              # 저장소 초기화
/shortcut:shortcut-add                           # 단축키 추가
/shortcut:shortcut-delete <app> <shortcut>       # 단축키 삭제
/shortcut:shortcut-search <keyword>              # 검색
/shortcut:shortcut-learn [app]                   # 학습 시작
/shortcut:shortcut-stats [app]                   # 통계 보기
/shortcut:shortcut-list                          # 앱 목록 보기
/shortcut:shortcut-cheatsheet [output_path]      # A4 Cheat Sheet 생성
```

### 작동 방식

1. 저장소 초기화 (`/shortcut:shortcut-init ~/shortcuts`)
2. 대화형 워크플로우로 단축키 추가:
   - App, Category, Shortcut, Description 입력
3. Markdown 테이블로 자동 저장
4. Leitner Box 알고리즘으로 학습:
   - Box 1 (매일) → Box 2 (3일) → Box 3 (7일)
5. Git 자동 커밋

## 사용 예시

### 1. 저장소 초기화

```bash
# 새 저장소 생성
/shortcut:shortcut-init ~/my-shortcuts

# 결과:
# ✓ Created ~/my-shortcuts
# ✓ Initialized git repository
# ✓ Created .shortcut-master/config.json
```

### 2. 단축키 추가

```bash
/shortcut:shortcut-add

# 대화형 입력:
# App: vscode
# Category: Editing
# Shortcut: cmd+d
# Description: Select next occurrence

# 결과:
# ✅ Shortcut added successfully!
# - vscode_shortcuts.md 생성/업데이트
# - README.md 자동 업데이트
# - Git commit: "Add shortcut: vscode - Cmd+D"
```

**생성되는 파일 예시 (`vscode_shortcuts.md`):**

```markdown
# VS Code Shortcuts

## Editing

| Shortcut | Description |
|----------|-------------|
| Cmd+D | Select next occurrence |
| Cmd+Shift+L | Select all occurrences |
```

### 3. 단축키 검색

```bash
/shortcut:shortcut-search "comment"

# 결과:
# === Search Results for "comment" ===
#
# [VS Code]
#   Cmd+/         Toggle line comment        (Editing)
#   Cmd+K Cmd+C   Add line comment          (Editing)
#
# Found 2 shortcuts across 1 app.
```

### 4. 학습 시작

```bash
# 기본 Flash 모드
/shortcut:shortcut-learn vscode

# Quick 모드 (빠른 학습)
/shortcut:shortcut-learn vscode --mode=quick

# 모든 카드 학습 (복습 예정 무시)
/shortcut:shortcut-learn vscode --all
```

**Flash 모드 예시:**

```
=== Learning Mode: VS Code (Flash) ===
Box 1: 5 cards | Box 2: 3 cards | Box 3: 2 cards

[Question 1/10] Box 1
What does this shortcut do?

  Cmd+D

[Press Enter to reveal answer]

=== Answer ===
  Cmd+D → Select next occurrence

Did you remember correctly?
  [y] Yes - move to Box 2
  [n] No - stay in Box 1
```

### 5. 통계 확인

```bash
/shortcut:shortcut-stats vscode

# 결과:
# === Learning Statistics: VS Code ===
#
# Box Distribution:
#   Box 1: 5 cards (review now)
#   Box 2: 12 cards (next: 2026-01-18)
#   Box 3: 23 cards (next: 2026-01-22)
#
# Overall Accuracy: 85.3%
#   Correct: 142 / Incorrect: 24
#
# Most Difficult Shortcuts (Top 5):
#   1. Cmd+K Cmd+S - incorrectCount: 8
#   2. Cmd+Shift+F - incorrectCount: 5
```

### 6. 앱 목록 보기

```bash
/shortcut:shortcut-list

# 결과:
# === Registered Apps ===
#
# 1. vscode (25 shortcuts)
# 2. chrome (12 shortcuts)
# 3. figma (8 shortcuts)
#
# Total: 45 shortcuts across 3 apps
```

### 7. 단축키 삭제

```bash
/shortcut:shortcut-delete vscode "Cmd+D"

# 결과:
# ✓ Deleted shortcut: Cmd+D from vscode
# ✓ Updated vscode_shortcuts.md
# ✓ Removed from learning progress
# ✓ Committed: "Delete shortcut: vscode - Cmd+D"
```

### 8. Cheat Sheet 생성

```bash
# 기본 (체크박스 없음)
/shortcut:shortcut-cheatsheet

# 학습 진행상황 표시 (읽기 전용)
/shortcut:shortcut-cheatsheet --mode progress

# 직접 체크 가능 (브라우저용)
/shortcut:shortcut-cheatsheet ~/Desktop/shortcuts.html --mode interactive

# 결과:
# ✓ Cheat sheet generated: ~/Desktop/shortcuts.html
# Mode: 학습 진행상황 표시
# Opened in browser
```

**체크박스 모드:**

| 모드 | 설명 |
|------|------|
| `simple` (기본) | 체크박스 없음 |
| `progress` | 학습 진행상황 기반 (✓=Box3, △=Box2, □=Box1/미학습) |
| `interactive` | 브라우저에서 직접 체크 (localStorage 저장) |

**생성되는 Cheat Sheet:**
- A4 사이즈에 최적화된 HTML
- 앱별로 그룹화, 섹션별 구분
- 개별 키캡 스타일로 높은 가독성
- 인쇄 시 배경색 지원
- (progress/interactive 모드) 진행률 표시 및 체크박스

## 결과물

| 작업 | 내용 |
|------|------|
| 단축키 파일 | `{app}_shortcuts.md` |
| README | `README.md` (Summary + Quick Reference) |
| 학습 진도 | `.shortcut-master/learning-progress.json` |
| Git 커밋 | 자동 커밋 및 푸시 |

### README.md 자동 생성

단축키 추가 시 README.md가 자동으로 업데이트됩니다:
- **Summary**: 앱별 단축키 개수, 최근 수정일
- **Quick Reference**: 앱별 Top 5 단축키

## 학습 모드

| 모드 | 설명 | 키 입력 |
|------|------|---------|
| Flash (기본) | 플래시카드 방식 | 3번/문제 |
| Quick | 빠른 학습 | 2번/문제 |
| Typing | 직접 입력 | 실제 단축키 |

## 제한 사항

- Git 저장소 내에서만 실행 가능
- 학습 진도는 로컬 전용 (기기 간 동기화 불가)
- Typing Mode는 동시 누름만 지원 (시퀀스 불가)

## 라이선스

MIT License

## 관련 문서

- [SPEC.md](./SPEC.md) - 프로젝트 명세서
- [CLAUDE.md](./CLAUDE.md) - 개발자 가이드
