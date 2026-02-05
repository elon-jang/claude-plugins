---
author: ''
date: '2026-01-29'
embedding_id: Claude Code를 10개 이상 -1e4094a9
tags:
- claude-code
- ai-agent
- automation
- mcp
- hook
title: Claude Code를 10개 이상 동시에 돌리는 방법이 두 가지 있습니다. 하나는 앱이 알아서 해주고, 다른 하나는 창시자가 직접 쓰는
  방식이에요
url: https://bit.ly/4rwQJjh
---

Claude Code를 10개 이상 동시에 돌리는 방법이 두 가지 있습니다. 하나는 앱이 알아서 해주고, 다른 하나는 창시자가 직접 쓰는 방식이에요

---

Claude Squad와 Boris Cherny 방식. 둘 다 병렬 작업인데 철학이 완전히 다릅니다.

Claude Squad는 cs 명령어 하나로 시작하는 터미널 앱이에요. tmux로 세션 관리하고, Git Worktree도 자동으로 만들어줍니다. n 키 누르면 새 세션, 화살표로 전환, s 키로 PR. 입문자한테 딱이에요.

Boris는 iTerm2에서 탭 5개를 직접 관리합니다. 번호를 1-5로 붙이고 시스템 알림으로 입력 필요할 때 알려주게 설정해뒀어요

---

근데 Boris는 여기서 끝이 아닙니다.

웹에서[claude.ai/code를](https://bit.ly/4rwQJjh)5-10개 더 돌려요. 터미널 작업하다가 웹으로 넘기기도 하고, teleport로 왔다 갔다도 해요.

심지어 아침마다 폰에서 Claude iOS 앱으로 세션 몇 개 시작해두고, 나중에 체크인한다고 합니다.

총 15개 이상을 혼자 컨트롤하는 거죠

---

모델은 뭘 쓸까요?

Boris는 Opus 4.5 with thinking을 모든 작업에 씁니다. 느리고 무거운 모델인데요

이유가 있어요. steering을 덜 해도 되고 tool use가 좋아서, 결국 작은 모델보다 더 빠르다고 합니다. 수정하느라 시간 쓰는 게 더 손해라는 거죠

---

여러 Claude가 같은 파일 건드리면 충돌 안 나냐고요?

Boris 답변이 명확합니다. Each agent gets its own git checkout

각 에이전트마다 별도 git checkout을 줘요. Claude Squad도 똑같이 Git Worktree로 격리합니다. 이건 둘 다 같아요.

---

진짜 차이는 팀 지식 축적에 있습니다.

Boris 팀은[CLAUDE.md](https://bit.ly/4rySYCF)하나를 공유해요. Git에 체크인하고, 팀 전체가 일주일에 여러 번 업데이트합니다.

Claude가 뭔가 잘못하면 거기에 추가해요. 다음부터는 같은 실수 안 합니다.

코드 리뷰할 때 동료 PR에 @claude 태그 달아서[CLAUDE.md](https://bit.ly/4rySYCF)업데이트하라고 시키기도 해요. Compounding Engineering이라고 부르더라고요.

참고로 그 파일 크기는 2.5k 토큰입니다. bash 명령어, 코드 스타일, UI 가이드라인, 에러 핸들링, PR 템플릿 정도가 들어있대요.

---

작업 시작은 어떻게 할까요?

Boris는 대부분 Plan mode로 시작합니다. Shift+Tab 두 번이에요

PR이 목표면 Plan mode에서 Claude랑 계획을 주고받아요. 계획이 마음에 들면 auto-accept 모드로 바꾸고, 그러면 Claude가 보통 한 방에 끝낸다고 합니다.

좋은 계획이 정말 중요하다고 강조하더라고요

---

반복 작업은 slash command로 자동화합니다

Boris는 commit-push-pr 커맨드를 하루에 수십 번 씁니다. git status 같은 정보를 inline bash로 미리 계산해서 모델과 왔다 갔다 안 해도 되게 만들었어요

.claude/commands/에 넣어두면 Claude도 이 워크플로우를 쓸 수 있습니다

---

Subagents도 씁니다.

code-simplifier는 작업 끝나면 코드를 단순화해주고, verify-app은 Claude Code를 E2E 테스트해줘요.

slash command처럼 매 PR마다 하는 흔한 워크플로우를 자동화하는 거죠.

---

PostToolUse hook으로 코드 포맷팅도 자동화합니다.

Claude가 보통 잘 포맷된 코드를 뱉는데, 마지막 10%를 hook이 잡아줘요. 나중에 CI에서 포맷팅 에러 나는 걸 방지하는 거죠.

---

권한 관리는 어떻게 할까요?

Boris는 dangerously-skip-permissions를 안 씁니다.

대신 permissions로 안전한 bash 명령어를 미리 허용해둬요. .claude/settings.json에 넣어서 팀이랑 공유합니다.

---

MCP로 외부 도구도 연결합니다.

Slack MCP 서버로 검색하고 메시지 보내고, BigQuery로 분석 쿼리 돌리고, Sentry에서 에러 로그 가져오고. 설정은 .mcp.json에 넣어서 팀 공유해요.

Claude가 알아서 도구들을 써준다고 합니다.

---

장시간 작업은 어떻게 하냐고요?

세 가지 방법이 있대요. 첫째, Claude한테 끝나면 background agent로 검증하라고 프롬프트. 둘째, Stop hook으로 더 확실하게. 셋째, ralph-wiggum 플러그인.

샌드박스에서는 dontAsk 모드나 skip-permissions 써서 Claude가 막힘없이 작업하게 해요.

---

그리고 가장 중요한 팁.

Claude에게 자기 작업을 검증할 방법을 줘라. 이 피드백 루프가 있으면 결과물 품질이 2-3배 올라간다고 합니다.

Boris는[claude.ai/code에](https://bit.ly/4ry58f8)랜딩되는 모든 변경사항을 Claude Chrome extension으로 테스트해요. 브라우저 열고, UI 테스트하고, 코드가 작동하고 UX가 좋을 때까지 반복합니다.

검증 방법은 도메인마다 달라요. bash 명령어 하나일 수도 있고, 테스트 스위트일 수도 있고, 브라우저나 폰 시뮬레이터일 수도 있어요.

이걸 rock-solid하게 만드는 데 투자하라고 합니다.

---

Claude Squad는 이런 Boris 방식의 일부를 자동화해준 거예요.

Git Worktree 자동 생성, 세션 전환 UI, Diff 미리보기. 진입장벽을 확 낮춰줍니다.

근데[CLAUDE.md](https://bit.ly/4rySYCF)팀 공유, Hooks, Subagents, MCP 연동, 검증 워크플로우는 직접 구축해야 해요.

---

정리하면 이렇습니다.

Claude Squad는 빠른 시작. 설치하고 cs만 치면 바로 병렬 작업이에요.
Boris 방식은 팀 스케일. 지식 축적, 자동화, 검증 루프까지 갖춘 완전체입니다.

입문자는 Squad로 시작하고, 감 잡히면 Boris 방식 요소를 하나씩 붙여보세요. CLAUDE.md부터요.

---
## AI Notes
- **Summary**: Claude Squad와 Boris Cherny 방식. 둘 다 병렬 작업인데 철학이 완전히 다릅니다.
- **Topics**: general