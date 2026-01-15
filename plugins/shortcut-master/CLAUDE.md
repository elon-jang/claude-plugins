# Claude Code Development Guide: Shortcut Master

이 문서는 Claude Code가 Shortcut Master 플러그인을 개발하고 유지보수할 때 참고하는 가이드입니다.

## 프로젝트 개요

**목적**: 애플리케이션 단축키를 GitHub에 저장하고 Leitner Box 알고리즘으로 효과적으로 학습

**핵심 원칙**:
1. **단순함**: 캐싱 없음, 매번 파싱
2. **엄격함**: 형식 검증, 중복 거부
3. **일관성**: 단축키 표기법 자동 정규화
4. **효율성**: 키 입력 최소화 (Flash Mode 3번/문제)

## 아키텍처

### 모듈 구조

```
scripts/
├── utils.py          # 유틸리티 함수
├── repo_manager.py   # 저장소 관리
├── parser.py         # Markdown 파싱
├── formatter.py      # 테이블 정렬
├── integrity.py      # 데이터 정합성
├── search.py         # 검색 엔진
├── learning.py       # Leitner Box 알고리즘
└── cli.py            # CLI 진입점
```

### 데이터 흐름

```
user input → cli.py → repo_manager/parser → learning/search → output
                           ↓
                    integrity check → clean orphaned data
                           ↓
                    formatter → format tables → git commit
```

## 핵심 설계 결정

### 1. 복습 타이밍 (정확한 날짜 매칭)

**구현**: `utils.is_due_for_review()`

```python
def is_due_for_review(last_reviewed, box, intervals):
    next_review = lastReviewed + interval
    return today >= next_review
```

**중요**: `>` 가 아니라 `>=` 사용. 늦은 복습은 다음 주기로 대기.

**이유**: 사용자가 의도적으로 복습을 건너뛰지 않도록.

### 2. 박스 이동 (단계적 승급만)

**Quick Mode에서도 점프 불허**:
```python
# ✓ Correct
if response == '2':
    card.box = min(card.box + 1, 3)  # Gradual

# ✗ Wrong (no jump allowed)
if response == '3':
    card.box = 3  # Jump - NOT ALLOWED
```

**이유**: 학습 효과를 위해 단계적 검증 필요.

### 3. 세션 저장 (완료 시에만)

**구현**: `learning.py`의 `_save_session_progress()`는 세션 끝에만 호출.

**트레이드오프**:
- **장점**: 일관성, 트랜잭션 무결성
- **단점**: Ctrl+C 시 진행 내용 손실

**대안 고려 (미구현)**: 문제별 즉시 저장
- 장점: 중단 시에도 진도 유지
- 단점: 파일 I/O 증가, 부분 세션 데이터

### 4. 데이터 정합성 (자동 정리)

**구현**: `integrity.py`의 `clean_orphaned_progress()`

```python
def clean_orphaned_progress():
    # Parse all shortcuts from files
    valid_keys = set(...)

    # Remove progress entries not in files
    orphaned = set(progress.keys()) - valid_keys
    for key in orphaned:
        del progress[key]
```

**호출 시점**: 학습 세션 시작 시 (조용히 처리)

**이유**: 사용자가 Markdown 파일을 직접 수정해도 진도 데이터와 자동 동기화.

### 5. 검색 (캐싱 없음)

**구현**: 매번 파일 파싱

```python
def search(query):
    shortcuts_by_app = parse_all_shortcuts(repo_path)  # Re-parse every time
    ...
```

**이유**:
- 1000개 단축키도 1초 이내 파싱 가능
- 파일 수정 즉시 반영
- 코드 단순화

**성능 목표**: 1000개 기준 1초 이내 (달성 가능)

## 구현 가이드

### 새 명령어 추가

1. `cli.py`에 subparser 추가:
```python
parser_newcmd = subparsers.add_parser('newcmd', help='...')
parser_newcmd.add_argument('arg1')
parser_newcmd.set_defaults(func=cmd_newcmd)
```

2. 함수 구현:
```python
def cmd_newcmd(args):
    repo_path = find_repo_root()
    if not repo_path:
        console.print("[red]저장소가 초기화되지 않았습니다.[/red]")
        return

    # Implementation
    ...
```

3. Git 커밋 (선택):
```python
try:
    repo = repo_manager.get_repo()
    if repo:
        repo.index.add([...])
        repo.index.commit("...")
except Exception:
    pass  # Git is optional
```

### 파서 수정

**주의사항**:
- 엄격한 검증 유지 (에러 시 중단)
- 라인 번호 포함한 에러 메시지
- 단축키 표기법 정규화 필수

**예시**:
```python
def _parse_row(self, line, section, line_num):
    # ... validation ...
    if error:
        raise ValueError(f"{self.file_path.name}:{line_num} - {error}")

    # Normalize shortcut
    shortcut_normalized = normalize_shortcut(shortcut_raw)
    ...
```

### 학습 모드 추가

1. `learning.py`에 모드 추가:
```python
def _run_newmode(self, cards: list[LearningCard]) -> SessionStats:
    stats = SessionStats(...)

    for card in cards:
        # Show question
        # Get response
        # Update card
        # Update stats

    return stats
```

2. `start_session()`에서 호출:
```python
if mode == 'newmode':
    stats = self._run_newmode(cards)
```

3. CLI에서 선택지 추가:
```python
parser_learn.add_argument('--mode', choices=['flash', 'quick', 'typing', 'newmode'])
```

## 테스트

### 수동 테스트 시나리오

```bash
# 1. 초기화
/shortcut init ~/test-shortcuts
cd ~/test-shortcuts

# 2. 단축키 추가
/shortcut add
# App: vscode
# Category: Editing
# Shortcut: cmd+d
# Description: Select next occurrence

# 3. 파일 확인
cat vscode_shortcuts.md

# 4. 검색
/shortcut search "select"

# 5. 학습
/shortcut learn vscode

# 6. 파일 직접 수정 (정합성 테스트)
# vscode_shortcuts.md에서 Cmd+D 삭제
/shortcut learn vscode  # 진도 데이터 자동 정리 확인

# 7. 중복 테스트
/shortcut add
# 같은 단축키 입력 → 에러 확인

# 8. 표기법 정규화 테스트
/shortcut add
# Shortcut: cmd+shift+p → Cmd+Shift+P로 변환 확인
```

### 단위 테스트 (TODO)

```python
# tests/test_parser.py
def test_normalize_shortcut():
    assert normalize_shortcut('cmd+d') == 'Cmd+D'
    assert normalize_shortcut('command+shift+p') == 'Cmd+Shift+P'

# tests/test_learning.py
def test_is_due_for_review():
    # Box 1: 1일 경과
    # Box 2: 3일 경과
    # Box 3: 7일 경과
    ...
```

## 문제 해결

### 파싱 에러

**증상**: `vscode_shortcuts.md:15 - 테이블 형식 오류`

**원인**: Markdown 테이블 파이프(`|`) 누락 또는 컬럼 수 불일치

**해결**:
1. `parser.py`의 `_parse_row()` 확인
2. 필수 컬럼 3개: Shortcut, Description, Category
3. 각 행의 `|` 개수 확인

### Git 커밋 실패

**증상**: `Git 저장소 초기화 실패`

**원인**: Git이 설치되지 않았거나 저장소가 아님

**해결**:
1. Git 선택적 기능으로 설계 (실패 시 경고만)
2. `repo_manager.get_repo()`는 `Optional[git.Repo]` 반환
3. 모든 Git 작업을 try-except로 감싸기

### 학습 진도 불일치

**증상**: 파일에 없는 단축키의 진도 데이터

**원인**: 사용자가 파일 직접 수정

**해결**:
1. `integrity.clean_orphaned_progress()` 자동 호출
2. 학습 시작 시 정리
3. 조용히 처리 (사용자에게 알리지 않음)

## 향후 개선 (TODO)

### 구현 필요

- [ ] `/shortcut delete` 완전 구현
- [ ] Typing Mode 실제 키보드 감지 (pynput)
- [ ] 단위 테스트 추가
- [ ] 학습 세션 중 Ctrl+C 처리 (임시 저장)

### 고려 사항

- **멀티 키 시퀀스 지원**: Cmd+K → Cmd+S
  - 파서 수정 필요
  - Typing Mode에서 타임아웃 로직 추가

- **이미지 첨부**: 단축키 스크린샷
  - Markdown에 이미지 링크 추가
  - 학습 시 이미지 표시

- **충돌 감지**: 같은 앱 내 중복 단축키 경고
  - `integrity.py`에 `check_conflicts()` 추가

## 코드 스타일

- **Type hints 사용**: 모든 함수에 타입 힌트
- **Docstring 작성**: 모든 public 함수/클래스
- **Rich 사용**: CLI 출력에 색상 및 포맷팅
- **에러 메시지**: 한글로 사용자 친화적

**예시**:
```python
def normalize_shortcut(shortcut: str) -> str:
    """
    Normalize shortcut notation to standard format.

    Examples:
        cmd+d -> Cmd+D
        command+shift+p -> Cmd+Shift+P

    Args:
        shortcut: Raw shortcut string

    Returns:
        Normalized shortcut in format: Cmd+Shift+P
    """
    ...
```

## 배포

### 플러그인 등록

1. `.claude-plugin/plugin.json` 업데이트
2. Marketplace에 등록
3. `README.md`의 설치 가이드 확인

### 의존성 관리

`requirements.txt`:
```
gitpython>=3.1.0
tabulate>=0.9.0
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.21.0
rich>=13.0.0
pynput>=1.7.0
```

**주의**: 버전 고정 최소화, 호환성 유지

## 참고 자료

- [SPEC.md](./SPEC.md) - 프로젝트 명세서
- [README.md](./README.md) - 사용자 가이드
- [Leitner System](https://en.wikipedia.org/wiki/Leitner_system) - 학습 알고리즘 이론
