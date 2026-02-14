---
name: shortcut-search
description: 키워드로 단축키를 검색합니다 (YAML 직접 검색)
argument-hint: "<keyword>"
allowed-tools:
  - Grep
  - Read
  - Glob
---

# Search Shortcuts

키워드로 모든 앱의 단축키를 검색합니다.

## Constants

```
REPO_ROOT = ~/elon/ai/shortcut
YAML_DIR  = $REPO_ROOT/shortcuts
```

## Usage

```
/shortcut:shortcut-search <keyword>
```

## Workflow

### 1. YAML 파일 검색

Grep tool로 `$YAML_DIR/*.yaml` 파일들에서 keyword를 검색합니다.
- `description` 필드와 `shortcut` 필드 모두에서 검색
- 대소문자 구분 없이 검색 (`-i` flag)

### 2. 결과 파싱 및 표시

검색 결과를 앱별로 그룹핑하여 표시합니다:

```
🔍 "{keyword}" 검색 결과 ({n}건)

📝 Notion (2건)
  Cmd+K        → Add Link (선택한 텍스트에 링크 추가)
  Cmd+P        → Quick Find - 페이지명 입력해 즉시 이동

💬 Slack (1건)
  Cmd+K        → 퀵 스위처 - 채널/동료 이름 검색해서 바로 이동
```

매치된 YAML 파일을 Read로 읽어서 해당 항목의 전체 context(app name, section, shortcut, description)를 표시합니다.

### 3. 결과 없음

```
🔍 "{keyword}" 검색 결과가 없습니다.
유사한 검색어를 시도해보세요.
```

## Example

```
/shortcut:shortcut-search "탭"

🔍 "탭" 검색 결과 (6건)

🌐 Chrome (4건)
  Cmd+T         → 새 탭 열기
  Cmd+W         → 현재 탭 닫기
  Cmd+Shift+T   → 마지막으로 닫은 탭 다시 열기
  Ctrl+Tab      → 다음 탭으로 이동

🚀 Warp (2건)
  Ctrl+Tab      → 다음 탭
  Ctrl+Shift+Tab → 이전 탭
```
