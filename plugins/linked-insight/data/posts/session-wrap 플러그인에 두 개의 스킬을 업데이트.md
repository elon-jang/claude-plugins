---
author: ''
date: '2026-01-29'
embedding_id: session-wrap 플러그인에 두-99feaf8c
tags:
- claude-code
- ai-agent
- plugin
- hook
title: Claude Code와 나눴던 대화들 어떻게 하시나요?
url: https://bit.ly/4rlpEiS
---

Claude Code와 나눴던 대화들 어떻게 하시나요?
저는 그냥 두면 썩는다고 생각합니다. 대화 기록 하나하나가 자산이거든요.

그래서 무조건 뭔가로 남깁니다.
워크플로우로 깎아서 스킬로 만들거나.
인사이트를 추출해서 컨텍스트로 박아두거나.

그래서 제가 종종 사용하던 스킬들을 정리해서[정구봉 Goobong Jeong](https://bit.ly/4rlpEiS)님이 공유해주셨던 session-wrap 플러그인에 두 개의 스킬을 업데이트했습니다.

1. history-insight

Claude Code와 나눴던 대화들을 기간별로 분석하거나 프로젝트 단위로 빠짐없이 분석해서 원하는 인사이트를 뽑아줍니다.

"어제 하루 전체 세션에서 트러블슈팅 로그 분석해서 스킬로 만들 거 찾아줘"
"이번 달에 내가 가장 많이 했던 질문 종류 분석해줘"
"지난주 세션들에서 반복된 워크플로우 패턴 뽑아줘"

생각보다 파일 사이즈가 크고 bulky한 세션 로그들을 처리할 수 있도록 깎아두었어요.
세션 파일이 수백 개여도 병렬 배치 처리로 빠짐없이 분석합니다.

삽질했던 기록에서 스킬이 나오고.
자주 묻던 질문에서 컨텍스트가 나옵니다.

2. session-analyzer

스킬을 만들다 보면 점점 복잡해집니다.
서브에이전트 여러 개 호출하고, 페이즈 나누고, Hook 걸고.
복잡해질수록 예상대로 안 돌아가는 경우가 많습니다.

그래서 저는 스킬 만들면 꼭 Evaluation을 합니다.
원하는 동작을 했는지, 내부적으로 Hook, SubAgent, Tool Calling이 다 실행됐는지.
[SKILL.md](https://bit.ly/4ry5cLU)스펙 대비 실제 실행을 비교해서 Expected vs Actual 표로 뽑아줍니다.

세션 끝나면 그대로 두지마세요!
거기서 다음 워크플로우가 나옵니다.

plugins-for-claude-natives 여기에서 확인해보세요.
[https://lnkd.in/gguS9szH](https://lnkd.in/gguS9szH)

---
## AI Notes
- **Summary**: 저는 그냥 두면 썩는다고 생각합니다. 대화 기록 하나하나가 자산이거든요. 인사이트를 추출해서 컨텍스트로 박아두거나.
- **Topics**: general