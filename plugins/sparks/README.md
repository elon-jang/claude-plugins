# Sparks

지식과 인사이트를 Github에 저장하고, 소크라틱 대화/플래시카드/연결 탐색을 통해 학습하는 Claude Code 플러그인입니다.

## 설치

```bash
/plugin marketplace add elon-jang/claude-plugins
/plugin install sparks@claude-kit
```

## 사용법

### 명령어

```
/spark-init                             # 저장소 초기화
/spark-add                              # 새 지식 추가
/spark-blog                             # 블로그 포스트 저장
/spark-learn [--mode=MODE]              # 학습 시작
/spark-search <keyword>                 # 지식 검색
/spark-list [--stats]                   # 목록 조회
/spark-stats                            # 학습 통계 대시보드
```

### 작동 방식

1. 저장소 초기화 (`/spark-init`)
2. 대화형 워크플로우로 지식 추가:
   - 카테고리, 제목, 태그, 내용 입력
   - Q&A 자동 생성 및 확인
3. 학습 모드 선택:
   - Socratic: 단계별 Why/How 질문
   - Flashcard: Leitner 5-box 반복
   - Connect: 관련 지식 연결
4. Git 자동 커밋 & 푸시

## 결과물

| 작업 | 내용 |
|------|------|
| 지식 저장 | `{category}/{filename}.md` |
| 블로그 저장 | `blog/{filename}.md` |
| 학습 진도 | `.sparks/progress.json` |
| README 업데이트 | 자동 인덱싱 |

## 학습 모드

| 모드 | 설명 |
|------|------|
| Socratic | Claude가 5단계 질문으로 깊은 이해 유도 |
| Flashcard | Leitner 5-box 시스템 (1일→3일→7일→14일→30일) |
| Connect | 태그 기반 유사 항목 연결 및 인사이트 발견 |

## 저장소 구조

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

## 제한 사항

- Git 저장소 내에서만 실행 가능
- 학습 진도는 로컬 전용 (기기 간 동기화 불가)

## 라이선스

MIT License
