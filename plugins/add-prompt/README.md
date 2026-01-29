# add-prompt

Git 저장소에 새로운 AI 프롬프트를 자동으로 추가하고 Github에 푸시하는 Claude Code 플러그인입니다.

## 설치

```bash
/plugin marketplace add elon-jang/claude-plugins
/plugin install add-prompt@claude-kit
```

### 수동 설치

```bash
git clone https://github.com/elon-jang/claude-plugins.git
cd claude-plugins/plugins/add-prompt
```

## 사용법

### 명령어

```
/add-prompt
```

### 작동 방식

1. 저장소 구조 자동 감지 (카테고리, 브랜치)
2. 대화형 워크플로우 진행:
   - 카테고리 선택
   - 제목, 설명, 내용 입력
3. 자동 처리:
   - `.md` 파일 생성
   - README.md 업데이트 (알파벳 순 정렬)
   - Git commit & push

## 결과물

| 작업 | 내용 |
|------|------|
| 파일 생성 | `{category}/{filename}.md` |
| README 업데이트 | 자동 섹션 추가 및 정렬 |
| Git 커밋 | `Add new prompt: {title}` |
| Git 푸시 | 현재 브랜치에 자동 푸시 |

## 제한 사항

- Git 저장소 내에서만 실행 가능
- README.md 파일 필요
- 원격 저장소 설정 필요 (`origin`)

## 라이선스

MIT License
