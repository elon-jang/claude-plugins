# /shortcut

애플리케이션 단축키를 관리하고 학습하는 명령어입니다.

## Usage

```bash
/shortcut <subcommand> [options]
```

## Subcommands

### init
새 단축키 저장소를 초기화합니다.

```bash
/shortcut init [repo_path]
```

**예시**:
```bash
/shortcut init ~/shortcuts
```

### add
단축키를 대화형으로 추가합니다.

```bash
/shortcut add
```

프롬프트를 따라 앱, 카테고리, 단축키, 설명을 입력합니다.
- 단축키 표기법은 자동으로 정규화됩니다 (cmd+d → Cmd+D)
- 카테고리는 기존 카테고리에서 자동완성 제공
- 중복 단축키는 자동으로 거부됩니다

### search
키워드로 단축키를 검색합니다.

```bash
/shortcut search <keyword> [--section=<name>]
```

**예시**:
```bash
/shortcut search "comment"
/shortcut search "toggle" --section=Editing
```

### learn
학습 세션을 시작합니다.

```bash
/shortcut learn [app_name] [--mode=flash|quick|typing] [--all]
```

**학습 모드**:
- `flash` (기본): 플래시카드 방식 (Enter → y/n → Enter)
- `quick`: 빠른 학습 (Enter → 1/2)
- `typing`: 실제 단축키 입력 (동시 누름만 지원)

**예시**:
```bash
/shortcut learn vscode
/shortcut learn vscode --mode=quick
/shortcut learn vscode --all  # 모든 카드 강제 복습
```

### stats
학습 통계를 표시합니다.

```bash
/shortcut stats [app_name]
```

**표시 내용**:
- Box 분포
- 전체 정답률
- 가장 어려운 단축키 Top 5

### list
등록된 앱 목록을 표시합니다.

```bash
/shortcut list
```

### delete
단축키를 삭제합니다.

```bash
/shortcut delete <app_name> <shortcut>
```

**예시**:
```bash
/shortcut delete vscode "Cmd+D"
```

### rename
앱 이름을 변경합니다. 파일명과 학습 진도 데이터를 일괄 변경합니다.

```bash
/shortcut rename <old_name> <new_name>
```

**예시**:
```bash
/shortcut rename vscode vscode-insiders
```

## Implementation

이 명령어는 Python CLI 도구로 구현되어 있습니다:
- Entry point: `scripts/cli.py`
- Repository: https://github.com/elon-jang/claude-plugins/tree/master/plugins/shortcut-master

## Notes

- 저장소가 초기화되지 않은 경우 대부분의 명령어는 `/shortcut init`을 먼저 실행하라는 메시지를 표시합니다
- Git 저장소로 자동 관리되며, 단축키 추가/삭제/변경 시 자동 커밋됩니다
- 학습 진도는 로컬에만 저장되며 Git에 커밋되지 않습니다 (.gitignore에 포함)
