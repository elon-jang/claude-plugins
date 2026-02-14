---
name: shortcut-cheatsheet
description: A4 인쇄용 Cheat Sheet HTML을 생성합니다
argument-hint: "[output_path] [--mode simple|progress|interactive]"
allowed-tools:
  - Read
  - Write
  - Glob
---

# Generate Cheat Sheet

A4 한 장 분량의 인쇄용 Cheat Sheet HTML 파일을 생성합니다.

## Usage

```
/shortcut:shortcut-cheatsheet [output_path] [--mode MODE]
```

## Arguments

- `output_path` (optional): 출력 파일 경로. 기본값: `./cheatsheet.html`
- `--mode MODE` (optional): 체크박스 모드 선택
  - `simple` (기본값): 체크박스 없음
  - `progress`: progress.json 기반 색상 코딩 (마스터 현황 반영)
  - `interactive`: 직접 체크 가능 (브라우저 localStorage 저장)

## Implementation

Python 스크립트를 사용하지 않고, Claude Code의 Read/Write/Glob 도구로 직접 구현합니다.

### Step 1: 데이터 로드

1. `shortcuts/*.yaml` 파일들을 Glob으로 찾고 Read로 읽기
2. `--mode progress`인 경우 `progress.json`도 Read로 읽기

### Step 2: HTML 생성

A4 최적화 HTML 파일을 Write 도구로 생성.

### Step 3: 모드별 처리

#### `simple` 모드
- 체크박스 없음
- 앱별 그룹, 키캡 스타일 디자인

#### `progress` 모드 (기본)
- progress.json 읽어서 각 단축키에 색상 표시
- 미학습 (progress에 없음): 회색 배경 `#e5e7eb`
- Box 1: 빨간색 점 `#ef4444`
- Box 2-3: 노란색 점 `#eab308`
- Box 4-5: 초록색 점 `#22c55e`
- 앱별 완료율 표시: `Chrome 3/15 (20%)`
- 단축키 키 형식: `{categoryId}:{categoryId}-{index}` (0-based)

#### `interactive` 모드
- 기존과 동일: 직접 체크 가능, localStorage 저장
- Memorization Tips + Pattern Analysis 섹션 포함
- 인쇄 시 팁 섹션 자동 숨김

### Step 4: 파일 저장 + 브라우저 열기

1. Write 도구로 HTML 파일 저장
2. 사용자에게 경로 안내

### HTML 구조 참고

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Shortcut Cheat Sheet</title>
  <style>
    @page { size: A4; margin: 8mm; }
    @media print { .no-print { display: none; } }
    body { font-family: -apple-system, system-ui, sans-serif; font-size: 9px; }
    .app-section { break-inside: avoid; margin-bottom: 8px; }
    .app-header { font-weight: 800; font-size: 11px; margin-bottom: 4px; }
    .shortcut-row { display: flex; align-items: center; gap: 6px; padding: 2px 0; }
    .key { display: inline-block; background: #1e293b; color: #e2e8f0; padding: 1px 5px;
           border-radius: 3px; font-family: 'SF Mono', monospace; font-size: 8.5px; font-weight: 600; }
    .desc { color: #475569; }
    .progress-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
    .completion { font-size: 8px; color: #94a3b8; margin-left: 4px; }
  </style>
</head>
<body>
  <!-- 앱별 섹션 반복 -->
</body>
</html>
```

### 키 포맷 변환

YAML의 `Cmd+Shift+P` → 개별 키캡으로 분리하여 `<span class="key">Cmd</span> + <span class="key">Shift</span> + <span class="key">P</span>` 형태로 렌더링.
