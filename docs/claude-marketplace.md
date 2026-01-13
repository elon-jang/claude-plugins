# Claude Marketplace

Claude Code 플러그인 마켓플레이스에 대한 설명입니다.

## 개요

이 저장소는 Claude Code용 플러그인들을 모아놓은 monorepo입니다. 각 플러그인은 `plugins/` 폴더 내에 독립적으로 관리됩니다.

## 구조

```
elon-plugins/
├── .claude-plugin/
│   └── marketplace.json    # 플러그인 레지스트리
├── plugins/
│   └── <plugin-name>/      # 각 플러그인
├── docs/                   # 문서
└── assets/                 # 공유 에셋
```

## marketplace.json

`marketplace.json`은 모든 플러그인을 등록하는 중앙 레지스트리입니다.

```json
{
    "name": "elon-plugins",
    "owner": { "name": "...", "email": "..." },
    "description": "...",
    "version": "1.0.0",
    "plugins": [...]
}
```

## 플러그인 목록

| 플러그인 | 설명 |
|---------|------|
| youtube-to-score | YouTube 피아노 연주 영상에서 악보를 자동 생성 |
