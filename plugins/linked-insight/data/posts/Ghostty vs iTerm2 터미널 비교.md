---
author: ''
date: '2025-01-30'
embedding_id: Ghostty vs iTerm2 터미-788d9f0d
tags:
- claude-code
- terminal
- ghostty
- iterm2
- gpu-acceleration
- productivity
title: 'Claude Code 터미널 선택: Ghostty vs iTerm2'
url: ''
---

Claude Code 쓰면서 터미널 뭐 쓰세요? 저는 iTerm2에서 Ghostty로 갈아탔는데, 생각보다 체감이 확 다르더라고요.

---

Mac Studio에서 Claude Code를 돌리면 출력량이 어마어마합니다. 코드 분석, diff, 에이전트 진행 상황까지 초당 수천 줄이 쏟아져요.

iTerm2로 쓸 때는 솔직히 버벅임이 있는지도 몰랐습니다. 근데 Ghostty로 바꾸고 나서야 알았어요. 아, 이게 렉이었구나.

---

둘의 가장 큰 차이는 렌더링 방식입니다.

iTerm2는 CPU로 화면을 그립니다. Ghostty는 GPU로 그려요. Mac Studio의 강력한 GPU를 Ghostty가 활용하면서 CPU는 온전히 Claude Code 처리에 집중할 수 있게 됩니다.

실제로 1GB 로그 파일 처리하거나 npm 빌드 출력 보여줄 때 Ghostty가 훨씬 부드럽습니다.

---

메모리 사용량도 차이가 납니다.

탭 여러 개 열어놓고 테스트해봤는데요. Ghostty는 약 129MB, iTerm2는 약 207MB를 먹더라고요.

Claude Code 세션 여러 개 돌리는 분들한테는 이 차이가 꽤 의미 있습니다.

---

근데 멀티 윈도우랑 분할 화면은 어떨까요?

걱정 안 하셔도 됩니다. Ghostty도 다중 윈도우, 탭, 분할 전부 지원해요. 네이티브 macOS 컴포넌트를 써서 오히려 더 깔끔합니다.

Cmd+D로 수평 분할, Cmd+Shift+D로 수직 분할. 익숙한 단축키 그대로 쓸 수 있어요.

---

그럼 알림은요? Claude Code가 작업 끝나면 알림 받을 수 있나요?

Ghostty 1.2 버전부터 벨 기능이 제대로 들어갔습니다. Dock 아이콘 바운스, 배지, 타이틀바에 벨 이모지까지 다 됩니다.

bell-features 설정에서 title, attention, system, audio 중에 원하는 거 켜면 돼요.

---

근데 진짜 쓸모 있는 건 Claude Code Hooks입니다.

settings.json에 Stop 훅을 걸어두면 Claude Code가 작업 끝날 때마다 알림이 옵니다. terminal-notifier 설치하고 설정해두면 macOS 알림 센터로 알림이 뜨거든요.

이렇게 하면 다른 작업하다가도 Claude가 끝났는지 바로 알 수 있어요. 더 이상 터미널 계속 쳐다보고 있을 필요 없습니다.

---

그럼 iTerm2는 버려야 하나요?

꼭 그렇진 않습니다. tmux 헤비 유저라면 iTerm2가 낫습니다. 네이티브 tmux 통합이 진짜 좋거든요. 탭이랑 pane을 tmux 세션으로 바로 변환할 수 있어요.

그리고 iTerm2는 Shell Integration 알림이 내장되어 있어서 설정 없이도 알림 받을 수 있습니다.

---

정리하면 이렇습니다.

Claude Code 대량 출력이 많다면 Ghostty. GPU 가속 덕분에 렉 없이 쓸 수 있어요.

tmux 워크플로우가 중요하다면 iTerm2. 네이티브 통합이 아직 대체 불가입니다.

둘 다 Claude Code 완벽 호환되고 알림도 설정 가능하니까, 본인 워크플로우에 맞는 걸 고르시면 됩니다.

---

AI(claude code, codex, gemini)hook 알림 기능을 제가 macOS앱으로 개발해서 배포했는데 완전 무료입니다 한번 써보세요: https://bit.ly/4rySYTb

---

고스티는 검색이 안돼서 다시 아이텀으로

---
## AI Notes
- **Summary**: Claude Code 사용 시 터미널 선택 가이드. Ghostty는 GPU 렌더링으로 대량 출력에 강하고 메모리 효율적(129MB vs 207MB). iTerm2는 tmux 통합과 내장 알림이 장점. Claude Code Hooks로 작업 완료 알림 설정 가능.
- **Topics**: claude-code, terminal, ghostty, iterm2, gpu-acceleration, productivity