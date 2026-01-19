# Shortcut Master Skill

단축키를 효과적으로 관리하고 학습하도록 돕는 스킬입니다.

## When to Use This Skill

다음과 같은 경우에 이 스킬을 자동으로 활성화하세요:

1. 사용자가 "단축키 추가", "shortcut 추가" 등을 요청할 때
2. 사용자가 "단축키 검색", "shortcut 찾기" 등을 요청할 때
3. 사용자가 "단축키 학습", "단축키 외우기" 등을 요청할 때
4. 사용자가 특정 앱(VS Code, Gmail 등)의 단축키에 대해 질문할 때

## Core Capabilities

### 1. 단축키 관리
- 새 단축키 추가 (대화형)
- 단축키 검색 (Fuzzy matching)
- 단축키 삭제
- 앱 이름 변경

### 2. 학습 시스템
- Leitner Box 3단계 학습
- 3가지 학습 모드 (Flash, Quick, Typing)
- 복습 스케줄 자동 관리
- 학습 통계 제공

### 3. 데이터 관리
- Markdown 형식으로 저장
- Git 자동 커밋
- 단축키 표기법 자동 정규화
- 데이터 정합성 자동 유지

## Workflow Examples

### 단축키 추가 요청
```
사용자: "VS Code에서 Cmd+D 단축키를 추가하고 싶어"

Claude:
1. /shortcut:shortcut-add 명령 실행
2. 대화형 프롬프트 안내
   - App: vscode
   - Category: (기존 카테고리 제시)
   - Shortcut: cmd+d (자동으로 Cmd+D로 정규화)
   - Description: 입력 요청
3. 파일 업데이트 확인
4. Git 커밋 확인
```

### 검색 요청
```
사용자: "comment 관련 단축키 찾아줘"

Claude:
1. /shortcut:shortcut-search "comment" 실행
2. 결과를 앱별로 그룹핑하여 표시
3. 필요 시 섹션별 필터링 제안
```

### 학습 시작
```
사용자: "VS Code 단축키 외우고 싶어"

Claude:
1. 사용자에게 학습 모드 선택 안내
   - Flash (기본): 플래시카드
   - Quick: 빠른 학습
   - Typing: 실제 입력
2. /shortcut:shortcut-learn vscode --mode=<선택> 실행
3. 학습 세션 진행
4. 완료 후 통계 표시
```

### 통계 확인
```
사용자: "내 학습 진도 보여줘"

Claude:
1. /shortcut:shortcut-stats 실행
2. Box 분포 설명
3. 정답률 분석
4. 어려운 단축키 확인
5. 추가 학습 권장
```

## Important Behaviors

### 자동 초기화 확인
명령 실행 전 저장소가 초기화되었는지 확인:
- 초기화 안 됨 → `/shortcut:shortcut-init` 실행 안내

### 표기법 정규화 설명
사용자가 소문자로 입력해도:
- `cmd+d` → `Cmd+D`로 자동 변환
- 변환 사실을 사용자에게 알림

### 학습 모드 추천
- **초보자**: Flash Mode (가장 간단)
- **빠른 복습**: Quick Mode
- **실전 연습**: Typing Mode (동시 누름만 지원 주의)

### 복습 타이밍 설명
"오늘 복습할 카드가 없습니다" 메시지 시:
- Leitner Box의 정확한 날짜 매칭 설명
- 다음 복습일 안내
- `--all` 플래그로 강제 복습 가능

### 데이터 정합성
- 파일 직접 수정 시 자동 정리 안내
- 중복 단축키 추가 시 거부 이유 설명

## Commands to Use

```bash
# 초기화
/shortcut:shortcut-init [repo_path]

# 관리
/shortcut:shortcut-add
/shortcut:shortcut-delete <app> <shortcut>
/shortcut:shortcut-rename <old> <new>
/shortcut:shortcut-list

# 검색
/shortcut:shortcut-search <keyword> [--section=<name>]

# 학습
/shortcut:shortcut-learn [app] [--mode=flash|quick|typing] [--all]

# 통계
/shortcut:shortcut-stats [app]
```

## Error Handling

### 저장소 미초기화
```
Error: 저장소가 초기화되지 않았습니다

→ /shortcut:shortcut-init ~/shortcuts 실행 권장
```

### 파싱 에러
```
Error: vscode_shortcuts.md:15 - 테이블 형식 오류

→ Markdown 테이블 형식 확인 안내
→ 필수 컬럼: Shortcut, Description, Category
```

### 중복 단축키
```
Error: 이미 존재하는 단축키입니다

→ /shortcut:shortcut-delete로 삭제 후 추가 안내
→ 또는 파일 직접 수정 제안
```

### 복습 카드 없음
```
오늘 복습할 카드가 없습니다. 다음 복습: Jan 18

→ Leitner Box 정확한 날짜 매칭 설명
→ --all 플래그로 강제 복습 가능
```

## Best Practices

1. **사용자 친화적 안내**
   - 에러 메시지 번역 및 해결 방법 제시
   - 다음 단계 명확히 안내

2. **학습 효과 극대화**
   - 적절한 학습 모드 추천
   - 정기적 복습 독려
   - 통계 기반 약점 분석

3. **데이터 무결성**
   - Git 커밋 자동화 확인
   - 파일 형식 검증
   - 백업 권장

4. **워크플로우 최적화**
   - 자주 사용하는 명령어 조합 제안
   - 단축키 그룹 관리 팁 제공

## Integration with Other Tools

- **Git**: 자동 버전 관리, 수동 push 안내
- **Markdown editors**: 파일 직접 수정 가능, 자동 정리
- **GitHub**: 원격 저장소 동기화 가이드

## Resources

- [SPEC.md](../../SPEC.md) - 프로젝트 명세서
- [README.md](../../README.md) - 사용자 가이드
- [CLAUDE.md](../../CLAUDE.md) - 개발자 가이드
