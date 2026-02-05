---
author: rascal-hyunjun
date: '2025-01-30'
embedding_id: Agentic Coding 도구 동향-ea402c67
tags:
- agentic-coding
- claude-code
- codex
- gemini-cli
- tool-comparison
- model-evolution
title: Agentic Coding 도구 동향 (Claude Code 출시 ~ 2026.01)
url: https://bit.ly/3NN925e
---

From Claude Code 출시부터 ~ 현재(26.01) 까지 파악한 Agentic Coding 도구들의 동향.

(여기서는 현재 주력으로 쓰이는 것들만 언급했습니다, 중간에 탈락한 도구들은 대부분 "가성비" 에서 떨어졌습니다)

## Claude Code

Sonnet 3.5 부터 의미있는 결과물 도출 시작, MCP 연동으로 날개를 달았음. Sonnet 3.7 에서 Tool Calling 성능이 향상되며 꽤나 자동으로 잘 동작.

Sonnet 4 에서 완전히 자리를 잡았으나 200K Context 에 고통받고 있었는데, 해결할 방법이 별로 없었음. 아직까지는 인간이 디테일하게 작업을 명령해야된다는건 동일. Sonnet 4 에서 1M 이 처음 등장했고, 처음 풀렸을 땐 꽤 재밌었으나 여전히 200K 가 넘어가는 시점에서 엄청난 환각으로 실제 체감은 별로였음.

근데 이미 Sonnet 3.7부터 나만의 개발 워크플로우를 만들어보기 시작했습니다.

**Opus 4.1**: 본격적인 대 CC 시대를 열게 된 모델이고 CC 도 그 즈음 본격적으로 돌아가주기 시작했습니다. 이게 2025.08 정도인 것 같네요.

**Sonnet 4.5**: God, 가격 - 속도 - 퀄리티 뭐 하나 빠지는 것 없이 잘 동작해주는 제대로 된 모델. 단, MCP Tool Explosion 에 속수무책으로 당함.

**2025.11 Opus 4.5**: GodGod, Output Token 가격이 1/3 로 떨어지는 무시무시한 상황이 나오고 그 사이 CC 도 많이 발전해서 내부 도구 호출과 MCP 도구를 적절하게 (조금) 넣어주면 아주 잘 동작!

11월 Opus4.5 이후로 지금까지 그간 깎아온 Harness 들이 힘을 받기 시작한거 같아요.

---

## Codex

gpt-5-codex 모델이 출시되며 경쟁 시작. 처음엔 CC 의 Limit 정책에 반발하며 Codex 로 대거 이주. 써보니 처음에는 꽤 괜찮다고 생각했는데 점점 복잡한 Tool Calling 에서 아쉬움을 드러냄.

**gpt-5.1 / gpt-5.1-codex**: 미안... 너무 별로였고, high - max(xhigh) 너무 느리고 답변도 별로였음.

**gpt-5.2 / gpt-5.2-codex**: GodGod, ChatGPT Plus 요금제($20) 만으로도 체감상 CC Max $100 에 버금가는 용량을 제공해준 것 같습니다. 물론 에이전틱 성능도 엄청나게 올라갔고 모델 자체의 원래 가진 지능이 높다보니 주어진 상황에 대한 "판단" 능력이 매우 뛰어나 졌습니다.

드디어 Workflow 에 제대로 된 Reflection + 비판 및 보충 설명을 담당해줄 모델이 등장했고 Codex 또한 발빠르게 CC 에서 추가된 기능들을 차근차근 흡수했습니다.

---

## Gemini CLI & Antigravity

Gemini 3 Pro 가 나왔지만 코딩은 흠? High 를 써도 논리성이 흐음... 너무 아쉬웠고 일단 Tool Calling 이 너무 안됐습니다.

Gemini 3 Flash 는 반대로 작은데 빠르고 코딩도 적절한 난이도에서 꽤나 하고 Tool Calling 도 준수했어요. 강점은 Multi Modality + Gemini 3 모델은 기본 WebSearch 가 내장!!

Anthgravity 는 나노바나나 때문에 주목을 받았고 Agent Manager 와 Task Specification Docs 에 Comment 하는 기능 때문에 좋았던거 같아요. 근데 그 외 장점을 모르겠습니다.

그리고 IDE 자체가 너무 무거웠습니다. 최근에 가격 정책이 타이트해지면서 더 눈길이 안가네요.

---

## GLM-4.6 / 4.7

준수한 성능, 아주아주 저렴한 가격. 오 이정도라면 미쳤는데? 하면서 잘 썼는데 20일인가요? Rate Limit 정책이 너무 빡빡해졌습니다. 동시 호출이... ㅠ

1년 플랜 주변에 추천도 많이 하고(프로모션이 있어서 1년 짜리를 $200불 초반에 샀죠. 저도 잘 쓰고 있고 그랬는데 치명타를 입었습니다)

이제 이 친구는 저에게 VSCode Extension 중 Roo Code 에 붙여서 쓰게 되는 모델이 되어버렸어요. 한계가 뚜렷해버려서 아주 작은 에러 처리용도 + 아주 단순한 형태의 코드 찍어내는 반복 작업용.

---

## 숨은 강자들

사람들이 잘 모르는 Qwen-Code / Mistral CLI 도 "공짜로" 아직까지도 잘 달달하게 잘 쓰고 있습니다.

GLM 결제 전에 제 단순한 코드 생성의 주역은 이 둘에다가 Cerebras 에서 제공해주는 API 로 정말 정신없이 빠른 코딩 했습니다.

Mistral CLI 는 은근히 내부에서 Mistral OCR 이 도는지 복잡한 문서 인식도 꽤나 잘 하더라구요. 주로 자료조사 많이 시켰습니다.

---

## 결론

쓰고 보니 참 다양한 툴들을 직접 써보며 불편함도 편리함도 그리고 공짜의 아쉬움도 다 느껴본 것 같네요.

어차피 도구는 바뀌면 적응하면 금방이고 또 요즘은 그 적응 자체가 서로 이식하기 쉽게 되어 있다보니 금방금방 옮겨다닐 수 있는 것 같습니다.

Cursor, Windsurf, 그리고 Copilot Pro 는 IDE 기반이다 보니 불편했고 가성비가 안맞더라구요. (최근에 Copilot 이 CLI 도 내고, 가격에 비해 모델 사용량이 꽤나 된다고 하더라구요. 근데 이미 정착했고 잘 쓰고 있어서 ㅎㅎㅎ)

**Claude Code + Codex + Gemini CLI 3종 세트로 정착했습니다.**
OpenCode 는 이들을 엮어주는 좋은 Harness 로 쓰고 있구요^^

그대신 언제든 이사갈 수 있게 계속 수정하고 발전시키면서 공통화 된 기능들은 최대한 서로서로 호환되도록 해놓고 있습니다. 언제 또 가격 정책을 바꿀지 모르잖아요!

---
## AI Notes
- **Summary**: Agentic Coding 도구 진화 타임라인. Claude Code는 Sonnet 3.5→Opus 4.5로 성숙, Codex는 gpt-5.2에서 가성비 폭발, Gemini CLI는 Flash가 강점. GLM은 Rate Limit으로 하락, Qwen-Code/Mistral CLI는 무료로 준수. 최종 정착: Claude Code + Codex + Gemini CLI 3종 세트 + OpenCode Harness.
- **Topics**: agentic-coding, claude-code, codex, gemini-cli, tool-comparison, model-evolution