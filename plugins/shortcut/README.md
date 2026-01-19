# Shortcut Master

애플리케이션 단축키를 GitHub에 저장하고, Leitner Box 시스템으로 효과적으로 학습할 수 있는 개인 단축키 관리 플러그인입니다.

## 설치

```bash
/plugin marketplace add elon-jang/claude-plugins
/plugin install shortcut@ai-plugins
```

### 수동 설치

```bash
git clone https://github.com/elon-jang/claude-plugins.git
cd claude-plugins/plugins/shortcut
pip install -r requirements.txt
```

## 사용법

### 명령어

```
/shortcut-init [repo_path]              # 저장소 초기화
/shortcut-add                           # 단축키 추가
/shortcut-delete <app> <shortcut>       # 단축키 삭제
/shortcut-search <keyword>              # 검색
/shortcut-learn [app]                   # 학습 시작
/shortcut-stats [app]                   # 통계 보기
/shortcut-list                          # 앱 목록 보기
```

### 작동 방식

1. 저장소 초기화 (`/shortcut-init ~/shortcuts`)
2. 대화형 워크플로우로 단축키 추가:
   - App, Category, Shortcut, Description 입력
3. Markdown 테이블로 자동 저장
4. Leitner Box 알고리즘으로 학습:
   - Box 1 (매일) → Box 2 (3일) → Box 3 (7일)
5. Git 자동 커밋

## 결과물

| 작업 | 내용 |
|------|------|
| 단축키 파일 | `{app}_shortcuts.md` |
| README | `README.md` (Summary + Quick Reference) |
| 학습 진도 | `.shortcut-master/learning-progress.json` |
| Git 커밋 | 자동 커밋 및 푸시 |

### README.md 자동 생성

단축키 추가 시 README.md가 자동으로 업데이트됩니다:
- **Summary**: 앱별 단축키 개수, 최근 수정일
- **Quick Reference**: 앱별 Top 5 단축키

## 학습 모드

| 모드 | 설명 | 키 입력 |
|------|------|---------|
| Flash (기본) | 플래시카드 방식 | 3번/문제 |
| Quick | 빠른 학습 | 2번/문제 |
| Typing | 직접 입력 | 실제 단축키 |

## 제한 사항

- Git 저장소 내에서만 실행 가능
- 학습 진도는 로컬 전용 (기기 간 동기화 불가)
- Typing Mode는 동시 누름만 지원 (시퀀스 불가)

## 라이선스

MIT License

## 관련 문서

- [SPEC.md](./SPEC.md) - 프로젝트 명세서
- [CLAUDE.md](./CLAUDE.md) - 개발자 가이드
