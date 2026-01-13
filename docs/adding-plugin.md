# 플러그인 추가 가이드

새로운 플러그인을 추가하는 방법을 설명합니다.

## 1. 플러그인 폴더 생성

```bash
mkdir -p plugins/<plugin-name>
```

## 2. 필수 파일 구조

```
plugins/<plugin-name>/
├── CLAUDE.md          # 플러그인 설명 및 사용법
├── README.md          # 플러그인 소개
├── skills/            # 스킬 정의 파일들
│   └── <skill>.md
└── scripts/           # 실행 스크립트 (선택)
```

## 3. marketplace.json에 등록

`.claude-plugin/marketplace.json`에 새 플러그인을 추가합니다:

```json
{
    "name": "<plugin-name>",
    "source": "./plugins/<plugin-name>",
    "description": "플러그인 설명",
    "keywords": ["keyword1", "keyword2"]
}
```

## 4. 플러그인 테스트

로컬에서 플러그인이 정상 작동하는지 테스트합니다.
