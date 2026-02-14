# PLAN — linked-insight 개선 사항

> 우선순위: P0(즉시) → P1(다음 세션) → P2(여유 시)

---

## 데이터 품질 (현황: 34개 글)

| 필드 | 커버리지 | 목표 |
|------|---------|------|
| author | 32.4% (11/34) | 100% |
| url | 70.6% (24/34) | 100% |
| published_date | 0% (0/34) | 가능한 만큼 |

### P0. 기존 글 published_date 백필

- [ ] URL 있는 24개 글: `fetch_post.py`로 재크롤링 → published_date 추출
- [ ] `backfill.py --apply`에 published_date 자동 채우기 로직 추가 (URL → 재크롤 → 날짜만 업데이트)
- [ ] URL 없는 10개 글: 수동 입력 또는 빈 문자열 유지

### P1. author 빈값 23개 해소

- [ ] URL 있는 글 중 author 빈값: `fetch_post.py` 재크롤로 author 추출 시도
- [ ] 재크롤 실패 시 수동 입력 목록 생성 (backfill --report 활용)
- [ ] slug 형태 author (예: `jyoung105`, `rascal-hyunjun`) → 실명 매핑 dict 추가

### P1. URL 빈값 10개 해소

- [ ] 제목/내용으로 LinkedIn 검색 → 원본 URL 수동 매칭
- [ ] 롱블랙 등 비-LinkedIn 소스는 별도 처리

### P2. 중복 URL 정리

- [ ] `bit.ly/4rlpEiS` 공유하는 3개 파일 → 실제 원본 URL 확인 후 개별 수정

---

## 기능 개선

### P1. backfill.py 자동화 강화

- [ ] `--apply` 모드에 published_date 자동 채우기 추가 (URL 있는 글 → fetch_post.py → 날짜만 추출)
- [ ] `--apply` 모드에 author 재추출 추가 (빈값 + URL 있는 경우)
- [ ] 재크롤 시 rate limit 고려 (글 사이 2~3초 sleep)

### P2. fetch_post.py 개선

- [ ] `--fields` 옵션: 특정 필드만 추출 (`--fields published_date,author`)
- [ ] `--update` 옵션: 기존 .md 파일에 빈 필드만 업데이트
- [ ] 쿠키 만료 감지 개선 (현재는 content 추출 실패로만 판단)

### P2. 검색 품질

- [ ] published_date 기반 시간순 정렬 옵션 추가 (`search.py --sort date`)
- [ ] author 필터 추가 (`search.py --author "이름"`)

---

## 완료

- [x] published_date 필드 추가 — fetch_post.py, linkedin-save.md, stats.py, backfill.py (2026-02-05)
- [x] backfill.py 생성 — 태그/날짜/파일명 자동 수정 + 리포트 (2026-02-05)
- [x] fetch_post.py author 추출 — 6 CSS selectors + meta + Korean regex (2026-02-05)
