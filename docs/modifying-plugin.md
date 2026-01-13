# 플러그인 수정 가이드

기존 플러그인을 수정하는 방법을 설명합니다.

## 1. 플러그인 위치

모든 플러그인은 `plugins/<plugin-name>/` 폴더에 있습니다.

## 2. 수정 가능한 항목

### 스킬 수정

- `skills/` 폴더 내의 `.md` 파일 수정
- 새로운 스킬 추가 또는 기존 스킬 삭제

### 스크립트 수정

- `scripts/` 폴더 내의 스크립트 파일 수정

### 메타데이터 수정

- `CLAUDE.md` 또는 `README.md` 업데이트

## 3. marketplace.json 업데이트

플러그인의 설명이나 키워드가 변경되면 `.claude-plugin/marketplace.json`도 함께 업데이트합니다.

## 4. 버전 관리

- 변경 사항은 루트의 `CHANGELOG.md`에 기록합니다
- 중요한 변경은 `marketplace.json`의 버전을 업데이트합니다
