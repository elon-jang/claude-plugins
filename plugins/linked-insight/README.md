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
# Gemini API 키 설정 (시맨틱 검색용)
export GOOGLE_API_KEY="your-api-key"

# 또는 .env 파일에 추가
echo 'GOOGLE_API_KEY=your-api-key' >> .env
```

API 키 발급: https://aistudio.google.com/apikey

## 사용법

### 스킬

| 명령어 | 설명 |
|--------|------|
| `/linkedin-save` | LinkedIn 글 저장 (복사-붙여넣기 → frontmatter → 임베딩) |
| `/linkedin-search <검색어>` | 하이브리드 검색 (키워드 + 시맨틱) |
| `/linkedin-analyze` | 글 분석, 태그 분포, 인사이트 |

### CLI 직접 사용

```bash
cd /Users/elon/elon/ai/claude-code/claude-plugins/plugins/linked-insight

# 검색
python scripts/search.py "Claude Code" --mode hybrid --verbose

# 새 글 마이그레이션
python scripts/migrate.py --file "data/posts/새글.md"
```

## 디렉토리 구조

```
linked-insight/
├── .claude-plugin/
│   └── plugin.json          # 플러그인 설정
├── skills/
│   ├── linkedin-save/       # 글 저장 스킬
│   ├── linkedin-search/     # 글 검색 스킬
│   └── linkedin-analyze/    # 글 분석 스킬
├── scripts/
│   ├── embed.py             # Gemini 임베딩
│   ├── index.py             # ChromaDB 관리
│   ├── search.py            # 하이브리드 검색
│   └── migrate.py           # 마이그레이션
├── data/
│   ├── posts/               # 저장된 글 (frontmatter 포함)
│   ├── chroma/              # 벡터 DB
│   └── metadata.json        # 메타데이터 캐시
├── source/                  # 원본 파일 (마이그레이션 전)
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

## 라이선스

MIT
