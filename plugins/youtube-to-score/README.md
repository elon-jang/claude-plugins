# YouTube-to-Score

YouTube 피아노 연주 영상에서 악보(MIDI, MusicXML, PDF)를 자동 생성하는 Claude Code 플러그인입니다.

## 설치

```bash
/plugin marketplace add elon-jang/claude-plugins
/plugin install youtube-to-score@claude-kit
```

### 수동 설치

```bash
git clone https://github.com/elon-jang/claude-plugins.git
cd claude-plugins/plugins/youtube-to-score
./scripts/setup.sh
```

## 사용법

### 명령어

```
/youtube-to-score <youtube_url>
```

### 자연어 요청

```
"이 유튜브 피아노 영상을 악보로 만들어줘: https://youtube.com/watch?v=..."
"YouTube에서 피아노 채보해줘"
```

### 작동 방식

1. YouTube URL 입력
2. 오디오 추출 (yt-dlp)
3. 피아노 음원 분리 (Demucs)
4. 음표 인식 (Basic Pitch)
5. 악보 생성 (music21)

## 결과물

| 작업 | 내용 |
|------|------|
| 오디오 추출 | `downloads/*.wav` |
| 악보 생성 | `output/*.mid`, `*.xml`, `*.pdf` |

## 제한 사항

- 피아노 전용
- macOS 전용
- 최대 10분 영상

## 라이선스

MIT License
