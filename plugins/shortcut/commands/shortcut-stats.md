---
name: shortcut-stats
description: 통합 학습 통계를 표시합니다
argument-hint: "[app_name]"
allowed-tools:
  - Read
  - Glob
---

# Shortcut Statistics

통합 학습 통계를 progress.json에서 읽어 표시합니다.

## Usage

```
/shortcut:shortcut-stats [app_name]
```

- `app_name` (optional): 특정 앱 통계만 표시. 없으면 전체.

## Implementation

Python 스크립트를 사용하지 않고, Claude Code의 Read/Glob 도구로 직접 구현합니다.

### Step 1: 데이터 로드

1. shortcut 프로젝트 루트의 `progress.json`을 Read로 읽기
2. `shortcuts/*.yaml` 파일들을 Glob으로 찾고 Read로 읽어 전체 단축키 수 파악
3. `app_name`이 지정되면 해당 앱만 필터링

### Step 2: 통계 출력

다음 형식으로 출력:

```
📊 Shortcut 학습 현황
━━━━━━━━━━━━━━━━━━━━━━━

🎯 전체 진행: 45/128 리뷰됨 (35%)
🔥 스트릭: 5일 연속
📝 총 리뷰: 230회

📦 Box 분포
   Box 1 ████████████░░░░░░░░  28 (62%)  — 즉시 복습
   Box 2 ████░░░░░░░░░░░░░░░░   8 (18%)  — 1일 간격
   Box 3 ██░░░░░░░░░░░░░░░░░░   5 (11%)  — 3일 간격
   Box 4 █░░░░░░░░░░░░░░░░░░░   3 (7%)   — 7일 간격
   Box 5 ░░░░░░░░░░░░░░░░░░░░   1 (2%)   — 마스터

✅ 정답률: 72% (165/230)

📅 오늘 복습 대상: 12장

❌ 가장 어려운 단축키 Top 5
   1. vscode:Cmd+Shift+P — 0/5 (0%) — Box 1
   2. chrome:Cmd+Shift+T — 1/4 (25%) — Box 1
   3. slack:Cmd+K        — 2/6 (33%) — Box 1
   4. notion:Cmd+/       — 1/3 (33%) — Box 2
   5. gmail:E            — 2/5 (40%) — Box 1

🎮 Shortcut Pro에서 약한 단축키 집중 연습:
   cd ~/elon/ai/shortcut/app && npm run dev
```

### Step 3: 앱별 필터

`app_name`이 지정된 경우:
- 해당 앱의 단축키만 필터링
- 제목: "📊 {앱이름} 학습 현황"
- 나머지 형식 동일

### Box 분포 바 계산

- 바 길이: 20자
- 각 Box의 비율에 따라 `█` (filled) + `░` (empty) 배분
- 퍼센트는 리뷰된 단축키 중의 비율

### 가장 어려운 단축키 기준

1. 정답률 낮은 순 (attempts > 0인 것만)
2. 동률이면 attempts 많은 순 (더 많이 시도했는데도 어려운 것)
3. 최대 5개
