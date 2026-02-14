---
name: shortcut-master
description: 단축키 관리 및 학습 시스템 (YAML 단일 소스 + 웹앱 자동 동기화)
---

# Shortcut Master Skill

단축키를 YAML로 관리하고, Shortcut Pro 웹앱과 자동 동기화되는 시스템입니다.

## Architecture

```
YAML (shortcuts/*.yaml)  ← 단일 소스 (Single Source of Truth)
  ├→ Shortcut Pro 웹앱    (Vite 플러그인이 virtual module로 변환, 파일 변경 시 자동 리로드)
  ├→ cheatsheet.html      (A4 인쇄용)
  └→ CLI 커맨드            (추가/삭제/검색/목록)
```

**핵심**: YAML 파일을 수정하면 모든 곳에 자동 반영됩니다.

## Data Location

```
~/elon/ai/shortcut/               # 단일 Git 저장소
├── shortcuts/                     # YAML 데이터 (14개 앱, 128개 단축키)
│   ├── macos.yaml
│   ├── chrome.yaml
│   ├── vscode.yaml
│   └── ...
├── app/                           # Shortcut Pro 웹앱 (React + Vite)
│   ├── src/
│   ├── plugins/
│   │   └── yaml-shortcuts-plugin.js  # YAML → virtual:shortcuts 변환
│   └── package.json
├── cheatsheet.html                # A4 치트시트
└── cheatsheet-checklist.html      # 체크리스트 버전
```

## When to Activate

다음 경우에 자동 활성화:

1. "단축키 추가", "shortcut 추가" 요청
2. "단축키 검색", "shortcut 찾기" 요청
3. "단축키 삭제" 요청
4. "단축키 목록", "어떤 앱 있어?" 요청
5. 특정 앱의 단축키에 대해 질문할 때

## Commands

| Command | 용도 |
|---------|------|
| `/shortcut:shortcut-add` | 대화형 단축키 추가 → YAML 수정 → git push → 웹앱 자동 반영 |
| `/shortcut:shortcut-delete` | 단축키 삭제 |
| `/shortcut:shortcut-search <keyword>` | YAML에서 키워드 검색 |
| `/shortcut:shortcut-list [app]` | 앱/단축키 현황 표시 |
| `/shortcut:shortcut-cheatsheet` | A4 치트시트 HTML 생성 |

## YAML Format

```yaml
app: Chrome
shortcuts:
  - section: Tabs
    items:
      - shortcut: Cmd+T
        description: 새 탭 열기
      - shortcut: Cmd+W
        description: 현재 탭 닫기
```

## Shortcut Notation Rules

### 정규화
- `cmd`, `command` → `Cmd`
- `ctrl`, `control` → `Ctrl`
- `opt`, `option`, `alt` → `Opt`
- `shift` → `Shift`
- 영문자는 대문자: `d` → `D`
- `+`로 연결: `Cmd+Shift+P`

### 특수 표기
- 범위: `Cmd+1~9` (1부터 9까지)
- 대안: `Opt+Cmd+←/→` (왼쪽 또는 오른쪽)
- 특수키: `Esc`, `Return`, `Space`, `Tab`, `Delete`, `⌫`
- 화살표: `←`, `→`, `↑`, `↓`
- 따옴표: `"!"` (YAML 이스케이프 필요한 문자)

## Web App Integration

Shortcut Pro 웹앱은 Vite 플러그인(`yaml-shortcuts-plugin.js`)으로 YAML을 읽습니다:
- `virtual:shortcuts` 모듈이 `SHORTCUT_DATA`와 `CATEGORIES`를 export
- YAML 디렉토리를 watch하여 변경 시 자동 full-reload
- 입력 불가 단축키(`~`, `/` 대안, 마우스, `Fn`, `Insert`)는 `typeable: false`로 마킹
- 웹앱의 타이핑 모드에서 자동 필터링

**웹앱 dev 서버 실행**:
```bash
cd ~/elon/ai/shortcut/app && npm run dev
```

## Workflow Examples

### 단축키 추가
```
사용자: "Notion에서 Cmd+Shift+L 추가해줘 - 불릿 리스트 토글"

1. shortcuts/notion.yaml 읽기
2. 중복 확인
3. Editing 섹션에 항목 추가
4. git commit + push
5. 웹앱 자동 반영 안내
```

### 단축키 검색
```
사용자: "탭 관련 단축키 찾아줘"

1. 모든 YAML에서 "탭" 검색
2. 앱별 그룹핑하여 표시
```

### 단축키 삭제
```
사용자: "Chrome에서 Cmd+Y 삭제해줘"

1. shortcuts/chrome.yaml에서 Cmd+Y 찾기
2. 항목 삭제
3. git commit + push
```

## Important Behaviors

### 데이터 무결성
- 추가 시 항상 중복 확인
- YAML 문법 유지 (들여쓰기 2칸, 하이픈 + 공백)
- 빈 섹션은 삭제

### Git 자동화
- 모든 변경 후 자동 commit + push
- 커밋 메시지 형식: `Add shortcut: {App} - {Shortcut} ({Description})`

### 웹앱 연동
- YAML 변경 → Vite dev server가 감지 → 브라우저 자동 리로드
- 프로덕션 빌드 시에도 YAML에서 읽음 (빌드 타임 변환)
