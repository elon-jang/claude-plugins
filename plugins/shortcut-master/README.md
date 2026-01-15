# Shortcut Master

애플리케이션 단축키를 GitHub에 저장하고, 효과적으로 학습하고 검색할 수 있는 개인 단축키 관리 시스템입니다.

## 특징

- **Leitner Box 학습 시스템**: 과학적으로 입증된 간격 반복 학습
- **Markdown 기반 저장**: 사람이 읽기 쉽고 Git으로 버전 관리
- **Fuzzy 검색**: 오타를 허용하는 스마트 검색
- **3가지 학습 모드**: Flash, Quick, Typing 모드 지원
- **Git 자동화**: 변경사항 자동 커밋
- **크로스 플랫폼**: macOS/Linux 지원

## 설치

### Claude Plugin으로 설치 (권장)

```bash
/plugin marketplace add elon-jang/claude-plugins
```

### 수동 설치

```bash
git clone https://github.com/elon-jang/claude-plugins.git
cd claude-plugins/plugins/shortcut-master
pip install -r requirements.txt
```

## 빠른 시작

### 1. 저장소 초기화

```bash
/shortcut init ~/shortcuts
```

### 2. 단축키 추가

```bash
/shortcut add
```

대화형으로 단축키를 추가합니다:
- App: vscode
- Category: Editing
- Shortcut: cmd+d (자동으로 Cmd+D로 변환)
- Description: Select next occurrence

### 3. 검색

```bash
/shortcut search "comment"
```

### 4. 학습

```bash
/shortcut learn vscode
```

## 사용법

### 명령어 목록

```bash
# 초기화
/shortcut init [repo_path]              # 새 저장소 초기화

# 관리
/shortcut add                           # 단축키 추가
/shortcut delete <app> <shortcut>       # 단축키 삭제
/shortcut rename <old> <new>            # 앱 이름 변경
/shortcut list                          # 앱 목록 보기

# 검색
/shortcut search <keyword>              # 키워드 검색
/shortcut search <keyword> --section=<name>  # 섹션별 검색

# 학습
/shortcut learn [app]                   # 학습 시작
/shortcut learn [app] --mode=quick      # Quick 모드
/shortcut learn [app] --all             # 모든 카드 복습

# 통계
/shortcut stats [app]                   # 학습 통계 보기
```

### 학습 모드

#### Flash Mode (기본)
플래시카드 방식으로 학습합니다.
```bash
/shortcut learn vscode
```

**흐름**:
1. Enter → 답 보기
2. y/n → 자기 평가
3. Enter → 다음 문제

**키 입력**: 문제당 평균 3번

#### Quick Mode
빠른 학습 모드입니다.
```bash
/shortcut learn vscode --mode=quick
```

**흐름**:
1. Enter → 답 보기
2. 1/2 → 난이도 선택

**키 입력**: 문제당 평균 2번

#### Typing Mode
실제 단축키를 입력하여 학습합니다.
```bash
/shortcut learn vscode --mode=typing
```

**제한사항**: 동시 누름만 지원 (Cmd+Shift+P), 시퀀스 불가 (Cmd+K → Cmd+S)

### Leitner Box 시스템

```
Box 1 (매일)  →  Box 2 (3일마다)  →  Box 3 (7일마다)
```

- **정답**: 다음 박스로 이동
- **오답**: Box 1으로 이동
- **목표**: Box 3에 80% 이상 달성

### 파일 구조

```
~/shortcuts/                        # 사용자 저장소
├── vscode_shortcuts.md             # VS Code 단축키
├── gmail_shortcuts.md              # Gmail 단축키
├── chrome_shortcuts.md             # Chrome 단축키
├── .shortcut-master/
│   ├── config.json                 # 설정
│   └── learning-progress.json      # 학습 진도 (로컬 전용)
├── .gitignore                      # learning-progress.json 제외
└── README.md
```

### Markdown 형식

```markdown
# VS Code Shortcuts

## Editing

| Shortcut | Description | Category |
|----------|-------------|----------|
| Cmd+D | Select next occurrence | Selection |
| Cmd+Shift+L | Select all occurrences | Selection |
| Cmd+/ | Toggle line comment | Comment |
```

**필수 컬럼**:
- `Shortcut`: 단축키 조합 (`Cmd+Shift+P` 형식)
- `Description`: 기능 설명
- `Category`: 분류

**섹션 헤더** (`## Editing`):
- 섹션별 필터링 가능: `/shortcut search "toggle" --section=Editing`

### 단축키 표기법

자동으로 표준화됩니다:
- `cmd+d` → `Cmd+D`
- `command+shift+p` → `Cmd+Shift+P`
- `ctrl+alt+delete` → `Ctrl+Alt+Delete`

## 설정

### 복습 간격 변경

`.shortcut-master/config.json`:
```json
{
  "settings": {
    "boxIntervals": {
      "box1": 1,    # 1일
      "box2": 3,    # 3일
      "box3": 7     # 7일
    },
    "quizSize": 10,
    "defaultLearningMode": "flash"
  }
}
```

## 고급 사용법

### 여러 기기에서 사용

**단축키 파일 동기화** (권장):
```bash
# ~/.shortcuts에서
git add vscode_shortcuts.md gmail_shortcuts.md
git commit -m "Update shortcuts"
git push
```

**학습 진도는 로컬 전용**: `learning-progress.json`은 각 기기에서 독립적으로 관리됩니다.

### 섹션별 필터링

```bash
/shortcut search "toggle" --section=Editing
```

### 강제 전체 복습

```bash
/shortcut learn vscode --all
```

## 문제 해결

### 파싱 에러

```
vscode_shortcuts.md:15 - 테이블 형식 오류
```

**해결**: Markdown 테이블 형식을 확인하세요. 필수 컬럼 (`|` 구분):
- Shortcut
- Description
- Category

### 중복 단축키

```
Error: 이미 존재하는 단축키입니다
```

**해결**: 동일한 단축키가 이미 파일에 있습니다. 파일을 직접 수정하거나 `/shortcut delete`로 삭제 후 추가하세요.

### 복습할 카드 없음

```
오늘 복습할 카드가 없습니다. 다음 복습: Jan 18
```

**정상**: Leitner Box 시스템은 정확한 날짜 매칭을 사용합니다. 예정일에 다시 시도하세요.

**강제 복습**: `/shortcut learn vscode --all`

## 제한사항

- **플랫폼**: macOS/Linux (Windows는 WSL 권장)
- **학습 진도**: 로컬 전용 (기기 간 동기화 불가)
- **Typing Mode**: 동시 누름만 지원 (시퀀스 불가)
- **세션 중단**: Ctrl+C 시 진행 내용 손실 (세션 완료 후 저장)

## 기여

이슈와 풀 리퀘스트를 환영합니다!

Repository: https://github.com/elon-jang/claude-plugins

## 라이선스

MIT License

## 작성자

Elon Jang

## 관련 문서

- [SPEC.md](./SPEC.md) - 프로젝트 명세서
- [CLAUDE.md](./CLAUDE.md) - 개발자 가이드
