---
name: shortcut-list
description: 등록된 앱과 단축키 현황을 표시합니다
argument-hint: "[app_name]"
allowed-tools:
  - Glob
  - Read
---

# List Shortcuts

등록된 모든 앱과 단축키 현황을 표시합니다.

## Constants

```
REPO_ROOT = ~/elon/ai/shortcut
YAML_DIR  = $REPO_ROOT/shortcuts
```

## Usage

```
/shortcut:shortcut-list           # 전체 앱 요약
/shortcut:shortcut-list chrome    # 특정 앱 상세
```

## Workflow

### 전체 목록 (인자 없음)

1. Glob으로 `$YAML_DIR/*.yaml` 파일 목록 가져오기
2. 각 YAML 파일을 Read로 읽어 `app` 이름과 shortcut 개수, section 목록 추출
3. 테이블 형식으로 표시:

```
📋 단축키 현황 (14개 앱, 128개 단축키)

App              Shortcuts  Sections
─────────────────────────────────────
🍎 macOS              14   Search, File Management, Window Management, System
🌐 Chrome             15   URL & Address Bar, Tabs, Navigation
💻 VS Code             5   Command, Editing, View
💬 Slack              12   Messaging, Search, Navigation, Message Control, ...
📝 Notion             10   Navigation, View, Editing
📧 Gmail              10   Compose, Navigation, Actions
🚀 Warp               17   AI, Editing, Navigation, Workflow, View, Settings
⚡ Raycast             6   General, App Hotkeys
🤖 Claude Code         8   Session, Input, Editing
🧠 Claude Desktop      7   Global, General, Input
🪟 Rectangle          10   Window Position, Window Size, Multi Display
📸 Shottr              7   Screenshot, App, OCR
🎨 Grabbit             1   Link
⌨️  AULA F87 Pro        6   OS Mode, RGB Lighting
```

### 특정 앱 상세 (인자 있음)

1. 해당 YAML 파일 Read
2. 섹션별로 모든 단축키 표시:

```
💻 VS Code (5 shortcuts)

Command
  Cmd+Shift+P   → 명령어 팔레트 열기 (모든 기능 검색/실행)
  Cmd+P         → 파일 빠르게 열기 (Quick Open)

Editing
  Cmd+D         → 같은 단어 다중 선택 (Multi-Cursor)
  Option+↑/↓    → 코드 줄 위/아래로 이동

View
  Ctrl+`        → 터미널 열기/닫기
```
