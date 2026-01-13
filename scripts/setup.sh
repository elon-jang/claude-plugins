#!/bin/bash
# YouTube-to-Score 설치 스크립트
# Usage: ./scripts/setup.sh

set -e

echo "=== YouTube-to-Score 설치 ==="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 스크립트 위치 기준으로 프로젝트 루트 찾기
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "프로젝트 경로: $PROJECT_ROOT"
echo ""

# 1. OS 확인
echo "[1/4] 시스템 확인..."
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}오류: 이 도구는 macOS에서만 지원됩니다.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ macOS 확인됨${NC}"
echo ""

# 2. Homebrew 확인 및 시스템 의존성 설치
echo "[2/4] 시스템 의존성 설치..."
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}Homebrew가 설치되어 있지 않습니다. 설치 중...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# ffmpeg 설치
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg 설치 중..."
    brew install ffmpeg
else
    echo -e "${GREEN}✓ ffmpeg 이미 설치됨${NC}"
fi

# lilypond 설치
if ! command -v lilypond &> /dev/null; then
    echo "lilypond 설치 중..."
    brew install lilypond
else
    echo -e "${GREEN}✓ lilypond 이미 설치됨${NC}"
fi
echo ""

# 3. Python 가상환경 생성
echo "[3/4] Python 가상환경 설정..."
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
    echo -e "${GREEN}✓ 가상환경 생성됨${NC}"
else
    echo -e "${GREEN}✓ 가상환경 이미 존재함${NC}"
fi
echo ""

# 4. Python 패키지 설치
echo "[4/4] Python 패키지 설치..."
source venv/bin/activate
pip install --upgrade pip -q
pip install yt-dlp basic-pitch music21 onnxruntime "scipy<1.15" -q
echo -e "${GREEN}✓ Python 패키지 설치 완료${NC}"
echo ""

# 완료 메시지
echo "=== 설치 완료 ==="
echo ""
echo "사용법:"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}python skills/youtube-to-score/scripts/main.py \"YOUTUBE_URL\"${NC}"
echo ""
echo "또는 Claude Code에서:"
echo -e "  ${YELLOW}\"이 유튜브 피아노 영상을 악보로 만들어줘: https://youtube.com/...\"${NC}"
