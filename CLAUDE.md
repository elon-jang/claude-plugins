# CLAUDE.md

This file provides guidance to Claude Code when working with this monorepo.

## Overview

Claude Code 플러그인 모음 (AI-Native Product Items)

## Plugins

| 플러그인 | 설명 | 경로 |
|---------|------|------|
| youtube-to-score | YouTube 피아노 → 악보 변환 | `./plugins/youtube-to-score/` |

## Rules

- 각 플러그인은 `plugins/<plugin-name>/` 폴더에 위치
- 플러그인별 상세 가이드는 각 폴더의 `CLAUDE.md` 참조
- 새 플러그인 추가 시 `.claude-plugin/marketplace.json`에 등록 필수

## Structure

```
├── .claude-plugin/marketplace.json  # 플러그인 레지스트리
├── plugins/                          # 개별 플러그인들
├── docs/                             # 문서
└── assets/                           # 공유 에셋
```

## Documentation

- [플러그인 추가](./docs/adding-plugin.md)
- [플러그인 수정](./docs/modifying-plugin.md)
- [Marketplace 소개](./docs/claude-marketplace.md)
