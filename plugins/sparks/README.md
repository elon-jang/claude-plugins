# Sparks

지식과 인사이트를 Github에 저장하고, 소크라틱 대화/플래시카드/연결 탐색을 통해 학습하는 Claude Code 플러그인

## Features

- **지식 저장**: 인사이트를 구조화된 형태로 Github에 저장
- **소크라틱 대화**: Claude가 Why/How 질문으로 깊은 이해 유도
- **플래시카드 퀴즈**: Leitner 5-box 알고리즘 기반 반복 학습
- **연결 탐색**: 관련 지식을 연결하여 새로운 인사이트 도출

## Installation

```bash
/install sparks@ai-plugins
```

## Quick Start

### 1. 지식 저장소 초기화

```bash
# 새 저장소에서 실행
/spark-init
```

### 2. 지식 추가

```bash
/spark-add
```

Claude가 다음을 물어봅니다:
- 카테고리 (concepts, insights, skills, til)
- 제목
- 태그
- 내용

Q&A는 Claude가 자동 생성하고 확인을 요청합니다.

### 3. 학습하기

```bash
# 플래시카드 모드
/spark-learn --mode=flashcard

# 소크라틱 대화 모드
/spark-learn --mode=socratic

# 연결 탐색 모드
/spark-learn --mode=connect
```

### 4. 블로그 작성

```bash
/spark-blog
```

블로그 포스트를 `blog/` 디렉토리에 저장하고 README에 자동 인덱싱합니다.

### 5. 검색 & 목록

```bash
# 키워드 검색
/spark-search machine learning

# 태그로 필터
/spark-search --tag=ai

# 목록 조회
/spark-list --stats
```

### 6. 학습 통계

```bash
/spark-stats
```

카테고리별 분포, 신뢰도 레벨, 복습 현황, 오늘 복습할 항목 등을 대시보드로 표시합니다.

## Knowledge Repository Structure

`/spark-init` 실행 시 생성되는 구조:

```
my-sparks/
├── .sparks/
│   ├── config.json       # 설정
│   └── progress.json     # 학습 진행 (로컬)
├── concepts/             # 개념/이론
├── insights/             # 인사이트
├── skills/               # 실용 기술
├── til/                  # Today I Learned
├── blog/                 # 블로그 포스트
└── README.md             # 자동 생성 인덱스
```

## Learning Modes

### Socratic Mode

Claude가 단계적 질문으로 이해도를 깊게 합니다:

1. **Level 1**: 자신의 말로 설명
2. **Level 2**: 왜 중요한가?
3. **Level 3**: 어떻게 적용하나?
4. **Level 4**: 예외 상황은?
5. **Level 5**: 다른 개념과의 연결

### Flashcard Mode

Leitner 5-box 시스템:
- Box 1: 매일 복습
- Box 2: 3일마다
- Box 3: 7일마다
- Box 4: 14일마다
- Box 5: 30일마다

### Connect Mode

- 태그/키워드 기반 유사 항목 제안
- 관계 유형 선택 (선행 조건, 대안, 통합)
- 새 인사이트 발견 시 새 항목 생성

## Commands

| 명령어 | 설명 |
|--------|------|
| `/spark-init` | 저장소 초기화 |
| `/spark-add` | 새 지식 추가 |
| `/spark-blog` | 블로그 포스트 저장 |
| `/spark-learn` | 학습 시작 (소크라틱/플래시카드/연결) |
| `/spark-search` | 지식 검색 |
| `/spark-list` | 목록 조회 |
| `/spark-stats` | 학습 통계 대시보드 |

## License

MIT
