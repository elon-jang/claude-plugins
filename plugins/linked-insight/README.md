# linked-insight

LinkedIn 글을 저장하고 시맨틱 검색하는 Claude Code 플러그인입니다.

## 설치

### 방법 1: 로컬 설치 (개발용)

```bash
# 심볼릭 링크 생성
ln -s /Users/elon/elon/ai/claude-code/claude-plugins/plugins/linked-insight ~/.claude/plugins/local/linked-insight

# Claude Code 재시작
```

### 방법 2: Marketplace 등록 후 설치

```bash
# Marketplace 추가 (이미 추가된 경우 생략)
/plugin marketplace add elon-jang/claude-plugins

# 플러그인 설치
/plugin install linked-insight@claude-kit
```

## 환경 설정

```bash
# .env 파일에 추가
GOOGLE_API_KEY=your-api-key    # 시맨틱 검색용 (필수)
BITLY_TOKEN=your-bitly-token   # URL 단축용 (선택)
```

- Gemini API 키 발급: https://aistudio.google.com/apikey
- Bitly API 토큰 발급: https://bitly.com/a/settings/api (무료 tier 사용 가능)

## 사용법

### 커맨드

| 명령어 | 설명 |
|--------|------|
| `/linkedin-save` | LinkedIn 글 저장 (중복체크 → URL단축 → frontmatter → 임베딩) |
| `/linkedin-search <검색어>` | 하이브리드 검색 (키워드 + 시맨틱) |
| `/linkedin-analyze` | 글 분석, 태그 분포, 인사이트 |
| `/linkedin-stats` | 저장된 글 통계 조회 |
| `/linkedin-delete <파일명>` | 글 삭제 (파일 + 벡터DB) |

### CLI 직접 사용

```bash
cd /Users/elon/elon/ai/claude-code/claude-plugins/plugins/linked-insight

# 검색
python scripts/search.py "Claude Code" --mode hybrid --verbose

# 새 글 마이그레이션
python scripts/migrate.py --file "data/posts/새글.md"

# 통계 조회
python scripts/stats.py

# 글 삭제
python scripts/delete.py --list          # 목록 조회
python scripts/delete.py "파일명.md"      # 삭제

# URL 단축
python scripts/shorten_urls.py --file "data/posts/글.md" --verbose
python scripts/shorten_urls.py "긴 URL 포함 텍스트"
```

## 디렉토리 구조

```
linked-insight/
├── .claude-plugin/
│   └── plugin.json          # 플러그인 설정
├── commands/
│   ├── linkedin-save.md     # 글 저장 커맨드
│   ├── linkedin-search.md   # 글 검색 커맨드
│   ├── linkedin-analyze.md  # 글 분석 커맨드
│   ├── linkedin-stats.md    # 통계 조회 커맨드
│   └── linkedin-delete.md   # 글 삭제 커맨드
├── scripts/
│   ├── embed.py             # Gemini 임베딩
│   ├── index.py             # ChromaDB 관리
│   ├── search.py            # 하이브리드 검색
│   ├── migrate.py           # 마이그레이션
│   ├── stats.py             # 통계 생성
│   ├── delete.py            # 삭제 (파일 + DB)
│   └── shorten_urls.py      # URL 단축 (Bitly)
├── data/
│   ├── posts/               # 저장된 글 (frontmatter 포함)
│   ├── chroma/              # 벡터 DB
│   └── metadata.json        # 메타데이터 캐시
├── .env                     # API 키 (gitignore)
├── pyproject.toml           # Python 의존성
└── README.md
```

## 기술 스택

| 구성요소 | 선택 |
|---------|------|
| 임베딩 | Gemini text-embedding-004 |
| 벡터 DB | ChromaDB (로컬) |
| 검색 | RRF (Reciprocal Rank Fusion) |
| URL 단축 | Bitly API (선택) |

## 라이선스

MIT
