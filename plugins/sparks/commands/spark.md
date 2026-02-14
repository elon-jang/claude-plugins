---
name: spark
description: 지식 저장/학습/검색 통합 명령 (add, blog, log, learn, search, list, stats, init)
argument-hint: "<add|blog|log|learn|search|list|stats|init> [options]"
allowed-tools:
  - AskUserQuestion
  - Glob
  - Read
  - Write
  - Edit
  - Bash
---

# Spark - 지식/인사이트 통합 명령

$ARGUMENTS의 첫 번째 단어로 서브커맨드를 결정하고, 해당 워크플로를 실행한다.

## Subcommands

| 서브커맨드 | 설명 | 옵션 예시 |
|-----------|------|----------|
| `add`     | 지식/인사이트 저장 | |
| `blog`    | 블로그 글 저장 | |
| `log`     | 데일리 로그 에피소드 | `--style=diary\|bullet\|devlog\|narrative` |
| `learn`   | 학습 (3가지 모드) | `--mode=socratic\|flashcard\|connect --category=<name>` |
| `search`  | 검색 | `<keyword> --tag=<tag> --category=<cat>` |
| `list`    | 목록 조회 | `--category=<name> --stats --due` |
| `stats`   | 학습 통계 대시보드 | |
| `init`    | 저장소 초기화 | `[directory]` |

## Routing

1. $ARGUMENTS에서 첫 번째 단어를 서브커맨드로 추출한다
2. 나머지 단어들은 서브커맨드의 옵션으로 전달한다
3. 해당 워크플로 파일을 Read한다: `commands/spark-commands/{서브커맨드}.md`
4. 파일 내용의 워크플로를 **그대로 실행**한다

## No Arguments

$ARGUMENTS가 비어있으면 AskUserQuestion으로 서브커맨드를 선택한다:

```json
{
  "questions": [
    {
      "question": "어떤 작업을 하시겠습니까?",
      "header": "Spark",
      "multiSelect": false,
      "options": [
        {"label": "add", "description": "지식/인사이트 저장"},
        {"label": "blog", "description": "블로그 글 저장"},
        {"label": "log", "description": "데일리 로그 에피소드"},
        {"label": "learn", "description": "학습 (소크라틱/플래시카드/연결)"}
      ]
    }
  ]
}
```

두 번째 질문 (나머지 서브커맨드):

```json
{
  "questions": [
    {
      "question": "또는 다른 작업을 선택하세요:",
      "header": "More",
      "multiSelect": false,
      "options": [
        {"label": "search", "description": "키워드/태그/카테고리 검색"},
        {"label": "list", "description": "목록 조회"},
        {"label": "stats", "description": "학습 통계 대시보드"},
        {"label": "init", "description": "새 저장소 초기화"}
      ]
    }
  ]
}
```

**Note**: 위 두 질문을 하나의 AskUserQuestion 호출로 보내지 않는다. 첫 번째 질문에서 선택하면 바로 실행한다. "Other"를 선택한 경우에만 두 번째 질문을 보여준다.

## Examples

```bash
/spark add                           # 지식 저장
/spark blog                          # 블로그 저장
/spark log                           # 데일리 로그
/spark log --style=bullet            # 불릿 스타일 로그
/spark learn --mode=flashcard        # 플래시카드 학습
/spark learn --mode=socratic         # 소크라틱 대화
/spark search react hooks            # 검색
/spark search --tag=python           # 태그 검색
/spark list --stats                  # 통계 포함 목록
/spark list --due                    # 복습 예정 목록
/spark stats                         # 학습 대시보드
/spark init                          # 저장소 초기화
/spark init ~/my-sparks              # 특정 디렉토리에 초기화
```
