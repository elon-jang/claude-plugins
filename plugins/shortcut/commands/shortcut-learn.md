---
name: shortcut-learn
description: Leitner Box 학습 세션을 시작합니다
argument-hint: "[app] [--all]"
allowed-tools:
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - Glob
---

# Learn Shortcuts — Leitner Box Session

Leitner Box 알고리즘 기반 학습 세션을 Claude Code 네이티브로 실행합니다.

## Usage

```
/shortcut:shortcut-learn [app] [--all]
```

- `app` (optional): 특정 앱만 학습 (예: chrome, vscode). 없으면 전체.
- `--all`: Leitner 스케줄 무시하고 모든 카드 복습.

## Implementation

Python 스크립트를 사용하지 않고, Claude Code의 Read/Write/AskUserQuestion 도구로 직접 구현합니다.

### Step 1: YAML 데이터 로드

1. `shortcuts/*.yaml` 파일들을 Glob으로 찾기 (경로: shortcut 프로젝트 루트의 `shortcuts/` 디렉토리)
2. 각 YAML 파일을 Read로 읽어 단축키 목록 파싱
3. 인자로 `app`이 지정되면 해당 앱만 필터링

### Step 2: progress.json 로드

1. shortcut 프로젝트 루트의 `progress.json` 파일을 Read로 읽기
2. 파일이 없으면 초기 구조로 새로 생성:
   ```json
   {"version":"1.0.0","lastUpdated":"...","stats":{"totalReviews":0,"streak":0,"lastDate":null},"shortcuts":{}}
   ```
3. progress에 없는 단축키는 Box 1, attempts 0으로 자동 추가

### Step 3: 복습 대상 선택

1. 각 단축키의 `nextReview` 날짜와 오늘 날짜 비교
2. `nextReview <= today` 인 것만 선택 (`--all` 이면 전부)
3. Box 낮은 순 → attempts 적은 순으로 정렬
4. 최대 **10개** 선택
5. 선택할 게 없으면 "오늘 복습할 단축키가 없습니다. 내일 다시 확인하세요!" 출력 후 종료

### Step 4: 플래시카드 학습 루프

각 카드에 대해 AskUserQuestion을 사용하여 플래시카드 진행:

```
📝 [1/10] Chrome — 주소창 포커스
   현재 Box 2 | 정답률 75%

   기억나시나요?
```

옵션:
- **정답 보기** — 정답을 공개
- **건너뛰기** — 이 카드 스킵 (기록 없음)

정답 공개 후:

```
✅ 정답: Cmd + L

   기억했나요?
```

옵션:
- **기억남** — Box +1 (max 5)
- **모르겠음** — Box → 1

### Step 5: progress.json 업데이트

각 카드 결과에 따라:
- `box`: 정답→+1 (max 5), 오답→1
- `correct`: 정답이면 +1
- `attempts`: +1
- `lastReview`: 현재 ISO 날짜
- `nextReview`: Box별 간격 적용
  - Box 1: 즉시 (오늘)
  - Box 2: +1일
  - Box 3: +3일
  - Box 4: +7일
  - Box 5: +14일
- `stats.totalReviews`: +1
- `stats.streak`: 오늘 처음 학습이면 streak 갱신
- `stats.lastDate`: 오늘 날짜

Write 도구로 `progress.json` 저장.

### Step 6: 세션 요약

```
📊 세션 요약
   ━━━━━━━━━━━━━━━━━
   학습: 10장 | 정답: 8 | 오답: 2
   정답률: 80%

   ↑ 승급: chrome:Cmd+L (Box 2→3), vscode:Cmd+P (Box 1→2)
   ↓ 강등: slack:Cmd+K (Box 3→1)

   다음 복습: 내일 3장, 3일 후 5장

🎮 Shortcut Pro에서 실전 연습: cd ~/elon/ai/shortcut/app && npm run dev
📊 약한 단축키를 집중 연습해보세요!
```

### Key Format

progress.json의 단축키 키 형식: `{categoryId}:{shortcutId}`
- categoryId: YAML 파일명 (확장자 제외) — 예: chrome, vscode
- shortcutId: `{categoryId}-{index}` — 예: chrome-0, chrome-1

YAML의 단축키 ID는 `{파일명}-{순서번호}` 형식 (0-based).

### Leitner 간격 참조

| Box | 간격 |
|-----|------|
| 1 | 0일 (즉시) |
| 2 | 1일 |
| 3 | 3일 |
| 4 | 7일 |
| 5 | 14일 |
