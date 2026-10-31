# 공용 블로그 발행

Sparks 스킬은 글 작성과 명령 선택을 담당한다. `scripts/publish-blog.mjs`는 정본 저장소에서 전체 사이트를 빌드하고 기존 경로 보존을 확인한 후 배포한다. Cloudflare Pages 배포는 파일 추가 API가 아니라 사이트 전체 교체다.

## 한 사람이 사용하는 경우

Node.js 22 이상, 플러그인 의존성(`npm ci`), 인증된 Wrangler가 필요하다. Wrangler 버전은 팀 CI에서 고정한다.

정본 저장소 구조:

```text
blog/                       Markdown 원본
.sparks/config.json         publish 설정
.sparks/published.json      전체 발행 목록
.sparks/static/             정적 자산 (빌드 루트에 복사)
```

설정 예시:

```json
{
  "publish": {
    "projectName": "your-project",
    "branch": "master",
    "url": "https://your-project.pages.dev",
    "title": "Our Blog",
    "description": "Knowledge & Insights"
  }
}
```

CLI에는 다른 프로젝트나 브랜치를 임의로 주입하는 옵션이 없다. 정본 config에서 읽는다. 글 파일명만 추가하면 기존 access 설정을 유지하며, 새 글은 public이 기본이다. private 발행은 `글.md:private`로 명시한다. Cloudflare Access는 별도로 구성해야 한다.

```bash
# 기본값: 전체 빌드와 운영 경로 비교만 수행. manifest/production 변경 없음
node /path/to/sparks/scripts/publish-blog.mjs --repo /path/to/my-sparks --files "새글.md"

# 검증을 통과한 전체 사이트 배포
node /path/to/sparks/scripts/publish-blog.mjs --repo /path/to/my-sparks --files "새글.md" --deploy
```

`--repo` 생략 시 `~/.sparks/config.json`의 `defaultRepo`를 사용한다. 새 글을 임의 디렉터리에 둔 채 source 경로만 바꾸는 방식은 사용하지 않는다. CI에서는 항상 `--repo`를 지정한다.

검증 실패 시 manifest를 변경하지 않는다. 빌드 결과는 `.sparks/publish-*/site`에 남아 검토할 수 있다. 새 배포는 `/sparks-inventory.json`에 정적 경로 목록을 포함하므로 이후 발행에서는 이미지·비공개 페이지·목록 외 페이지의 삭제도 차단한다. 이 목록은 경로만 포함하지만 공개되므로 비공개 글 제목은 URL에 민감정보를 넣지 않는다.

구형 사이트에 inventory가 없으면 공개 목록의 글 경로만 비교한다. 첫 전환 전에 정본에 비공개 글과 정적 자산까지 모두 있는지 별도로 확인해야 한다. 숨은 경로를 공개 목록만으로 알아낼 수는 없다.

## 실패했을 때

- `Published source missing`: manifest에 있는 Markdown 원본을 정본 저장소에 복원한다.
- `Invalid manifest entry`: access는 정확히 `public` 또는 `private`여야 한다.
- `Existing paths missing`: 운영 사이트에는 있지만 빌드에 없는 경로다. 원본·자산·기존 URL을 복구한다. 같은 글의 slug를 바꾸는 것도 경로 삭제로 취급한다.
- `Broken local link`: `.sparks/static/`에 자산을 추가하거나 링크를 고친다. 다른 글 링크는 발행할 최종 URL을 사용한다.
- `EEXIST ... publish.lock`: 실행 중인 발행을 확인한다. 비정상 종료 후에는 프로세스가 없는 것을 확인하고 해당 lock 파일만 제거한다.
- 네트워크/운영 기준 조회 실패: 배포하지 않고 중단한다.

삭제를 허용하는 우회 옵션은 제공하지 않는다. 의도적인 글 삭제나 공개 범위 변경은 보존 정책과 기존 URL 처리를 검토하는 별도 작업이다. 새 사이트 최초 생성에만 빈 manifest와 `--bootstrap --deploy`를 사용할 수 있다. 응답 가능한 기존 사이트에는 보존 검사가 그대로 적용된다.

## 팀 공용 CI

블로그 전용 Git 저장소를 정본으로 사용하고 팀원은 글·자산·manifest를 PR로 추가한다. 빌더/CLI는 버전을 고정한 Sparks 패키지 또는 별도 checkout으로 공급한다. Cloudflare 토큰은 CI secret에만 보관한다. 로컬 수동 production 발행과 CI 발행을 병행하지 않는다.

다음 workflow는 정본 저장소 기준 예시다. `<...>` 값은 조직에 맞게 설정한다.

```yaml
name: Publish blog
on:
  push:
    branches: [master]
concurrency:
  group: blog-production
  cancel-in-progress: false
permissions:
  contents: read
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
        with:
          path: knowledge
      - uses: actions/checkout@v4
        with:
          repository: <organization/sparks-plugin-repository>
          ref: <reviewed-commit-sha>
          path: plugin
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
        working-directory: plugin/plugins/sparks
      - run: npm test
        working-directory: plugin/plugins/sparks
      - run: npm install --global wrangler@4.63.0
      - run: node plugin/plugins/sparks/scripts/publish-blog.mjs --repo knowledge --deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

CI 방식에서는 PR에 새 글과 manifest를 함께 반영한다. CI는 `--files`나 `--all` 없이 저장된 전체 발행 목록을 사용하므로 CI가 만든 manifest 변경을 다시 push할 필요가 없다. 배포 직전 운영 목록 변경을 재확인하지만 이것만으로 서로 다른 PC 사이의 원자적 잠금은 보장하지 않는다. 공용 발행은 반드시 하나의 CI queue로 직렬화한다.

정본 저장소 `.gitignore`에 다음을 추가한다:

```gitignore
.sparks/publish-*/
.sparks/publish.lock
```

이 예시 workflow는 자동 설치하거나 활성화하지 않는다. 정본 복구, CI 자격 증명, branch 보호 설정은 해당 저장소 운영자가 설정한다.
