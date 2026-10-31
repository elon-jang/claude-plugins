---
name: sparks
description: Use when writing or publishing Markdown blog posts with Sparks and Cloudflare Pages, adding posts to an existing pages.dev blog, or investigating missing posts after deployment.
---

# Sparks 블로그 발행

Cloudflare Pages는 배포 디렉터리 전체로 사이트를 교체한다. 새 글 하나만 빌드해서 production에 올리면 기존 글이 사라진다. 정본 저장소의 전체 발행 목록을 사용한다.

## 실행

1. 정본 경로를 사용자 지정 `--repo` 또는 `~/.sparks/config.json`의 `defaultRepo`에서 확인한다. 임시 manifest를 만들지 않는다.
2. 원본 글은 정본의 `blog/`, 정적 자산은 `.sparks/static/`에 저장한다. 공개 글에는 내부 주소·개인정보·비밀값을 그대로 옮기지 않는다.
3. 이 스킬 폴더에서 `npm ci`를 실행한다. Node.js 22 이상이 필요하다.
4. 검증 명령을 실행한다. `<skill-dir>`은 현재 `SKILL.md`가 있는 디렉터리다.

```bash
node <skill-dir>/scripts/publish-blog.mjs --repo <knowledge-repo> --files "새글.md"
```

5. 사용자가 발행을 요청했고 검증을 통과했다면 동일 명령에 `--deploy`를 추가한다. Wrangler 인증과 프로젝트 설정은 정본 저장소 기준으로 확인한다.
6. 배포 결과와 실제 운영 URL을 확인하고 보고한다. Git commit/push는 별도 요청 또는 저장소의 명시적 정책을 따른다.

## 중단 조건

- 기존 운영 경로 누락, 발행 원본 누락, 잘못된 manifest, 깨진 로컬 링크는 먼저 수정한다.
- Wrangler 직접 호출, 임시 manifest, 운영 HTML 수집으로 검증을 우회하지 않는다.
- `--all`은 미발행 글도 공개 대상으로 추가하므로 전체 발행 요청이 있을 때만 사용한다.
- private 발행은 `글.md:private`를 명시하고 Cloudflare Access 구성을 확인한다.
- 여러 사용자의 production 발행은 단일 CI queue로 직렬화한다. 로컬 lock만으로 PC 간 동시 배포를 막을 수 없다.

## 검증과 참고

`npm test`로 회귀 테스트를 실행한다. 실패 조건, 최초 전환 제약과 공용 CI 구성은 [발행 가이드](docs/publishing.md)를 읽는다. 기본 실행은 검증만 하며 production과 정본 manifest를 변경하지 않는다.
