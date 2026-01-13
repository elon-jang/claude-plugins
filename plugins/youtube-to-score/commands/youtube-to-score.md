---
name: youtube-to-score
description: YouTube 피아노 영상을 악보(MIDI, MusicXML, PDF)로 변환
arguments:
  - name: url
    description: YouTube 영상 URL
    required: true
---

YouTube 피아노 영상을 악보로 변환합니다.

## 실행 방법

다음 명령을 실행하여 YouTube 영상에서 악보를 추출하세요:

```bash
source venv/bin/activate
python skills/youtube-to-score/scripts/main.py "$ARGUMENTS.url"
```

## 실행 전 확인사항

1. 가상환경이 설정되어 있는지 확인 (`venv/` 폴더 존재)
2. 없다면 `./scripts/setup.sh` 실행

## 출력 파일

- `downloads/` - WAV 오디오 파일
- `output/` - MIDI, MusicXML, PDF 악보 파일

## 제한사항

- 피아노 전용 (다른 악기 미지원)
- 최대 10분 길이 (초과 시 첫 10분만 처리)
- macOS 전용
