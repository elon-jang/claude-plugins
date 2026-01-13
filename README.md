# YouTube-to-Score

YouTube 피아노 연주 영상에서 악보(MIDI, MusicXML, PDF)를 자동 생성하는 Claude Code 플러그인입니다.

## 설치

```bash
git clone https://github.com/elon-jang/youtube-to-score.git
cd youtube-to-score
./scripts/setup.sh
```

### Claude Plugin으로 설치

```bash
/plugins marketplace add elon-jang/youtube-to-score
```

## 사용법

Claude Code에서 자연어로 요청:

```
"이 유튜브 피아노 영상을 악보로 만들어줘: https://youtube.com/watch?v=..."
"YouTube에서 피아노 채보해줘"
```

또는 직접 실행:

```bash
source venv/bin/activate
python skills/youtube-to-score/scripts/main.py "YOUTUBE_URL"
```

## 결과물

| 폴더 | 파일 |
|------|------|
| `downloads/` | 추출된 오디오 (`.wav`) |
| `output/` | 악보 (`.mid`, `.xml`, `.pdf`) |

## 제한 사항

- 피아노 전용
- macOS 전용
- 최대 10분

## 라이선스

MIT License
