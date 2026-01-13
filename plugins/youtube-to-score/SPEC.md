# Project Specification: YouTube-to-Score

## Overview

YouTube 피아노 연주 영상의 오디오를 분석하여 악보(MIDI, MusicXML, PDF)를 자동 생성하는 CLI 도구입니다. 악보 제작자가 빠르게 초안 악보를 얻어 편집할 수 있도록 설계되었습니다.

## Target Users

- **주요 대상**: 악보 제작자
- **워크플로우**: YouTube에서 피아노 커버 → 초안 악보 생성 → MuseScore 등에서 편집/완성
- **기대 품질**: 80-90% 정확도의 초안 (세부 수정 필요)

## Technology Stack

| 구성 요소       | 기술                      | 비고                    |
| -------------- | ------------------------- | ----------------------- |
| Language       | Python 3.12+              | macOS 전용              |
| Audio Extraction| `yt-dlp` + FFmpeg         | 최고 품질 WAV           |
| Transcription  | `basic-pitch` (Spotify AI) | ONNX 백엔드             |
| Score Processing| `music21`                 | MusicXML 출력           |
| PDF Rendering  | LilyPond                  | 선택적 (미설치 시 경고) |
| Inference      | ONNX Runtime              | `nmp.onnx` 모델         |

## Architecture

### Pipeline Flow

```mermaid
YouTube URL → Downloader → Transcriber → Renderer → Output Files
                 ↓              ↓             ↓
            downloads/       output/       output/
             (WAV)          (MIDI)     (XML, PDF)
```

### Module Responsibilities

1. **Downloader** (`scripts/downloader.py`)
   - YouTube URL에서 오디오 추출
   - 최고 품질 WAV로 변환
   - 10분 초과 시 첫 10분만 추출
   - `noplaylist: True`로 플레이리스트 방지

2. **Transcriber** (`scripts/transcriber.py`)
   - basic-pitch AI로 오디오 → MIDI 변환
   - 피아노 전용 (다른 악기 미지원)
   - scipy.signal.gaussian 호환성 패치 포함
   - **개선된 오디오 전처리**:
     - 하이패스 필터 (30Hz) - 저주파 노이즈 제거
     - 노이즈 제거 (noisereduce)
     - 오디오 정규화 (librosa)
   - **튜닝된 basic-pitch 파라미터**:
     - onset_threshold: 0.5
     - frame_threshold: 0.3
     - minimum_note_length: 58ms

3. **Renderer** (`scripts/renderer.py`)
   - MIDI → MusicXML 변환 (music21)
   - PDF 렌더링 시도 (LilyPond)
   - LilyPond 미설치 시 경고만 표시하고 XML/MIDI만 출력
   - **개선된 MIDI 후처리**:
     - 퀀타이즈 (16분음표, 셋잇단음표 그리드)
     - 옥타브 오류 수정
     - 피아노 범위 외 노트 필터링 (A0~C8)
     - 짧은 노트 필터링 (32분음표 이하)

## Input/Output Specifications

### Input

- **형식**: YouTube URL만 지원 (로컬 파일 미지원)
- **길이 제한**: 최대 10분
  - 초과 시: 자동으로 첫 10분만 처리하고 안내 메시지 표시
- **처리 방식**: 오디오 전처리 적용 (하이패스 필터, 노이즈 제거, 정규화)

### Output

- **생성 파일**: MIDI, MusicXML, PDF (모두 자동 생성)
- **파일명**: YouTube 영상 제목 그대로 사용 (특수문자 유지)
- **호환성**: MuseScore에서 정상 동작 확인 기준
- **후처리**: 없음 (basic-pitch + music21 기본 출력 그대로)

### Directories

- `downloads/`: 다운로드된 WAV 파일 (삭제 안 함)
- `output/`: 생성된 MIDI, XML, PDF 파일

## Error Handling

### 다운로드 실패

한글로 사용자 친화적 오류 메시지 제공:

| 오류 유형   | 메시지 예시                         |
| ----------- | ----------------------------------- |
| 저작권 차단 | "이 영상은 저작권으로 인해 다운로드할 수 없습니다." |
| 지역 제한   | "이 영상은 현재 지역에서 이용할 수 없습니다."       |
| URL 오류    | "올바른 YouTube URL을 입력해주세요."              |
| 네트워크 오류| "네트워크 연결을 확인해주세요."                   |

### PDF 렌더링 실패

- LilyPond 미설치/오류 시: 경고 메시지만 표시
- MIDI와 MusicXML은 정상 생성
- 예: "PDF 생성을 위해 LilyPond 설치를 권장합니다: brew install lilypond"

## CLI Interface

### Claude Code 명령

```bash
/youtube-to-score <youtube_url>
```

### 직접 실행

```bash
python skills/youtube-to-score/scripts/main.py "YOUTUBE_URL"
```

### 진행 상황 표시

현재 단계만 간단히 표시:

```
=== Phase 1: Downloading Audio ===
Audio downloaded: downloads/피아노커버.wav

=== Phase 2: Transcribing to MIDI ===
MIDI generated: output/피아노커버_basic_pitch.mid

=== Phase 3: Rendering Score ===
MusicXML saved to output/피아노커버_basic_pitch.xml
Score saved to PDF: output/피아노커버_basic_pitch.pdf

=== Pipeline Complete ===
```

## Constraints & Limitations

### 의도적 제한

- **악기**: 피아노 전용 (다른 악기 미지원)
- **플랫폼**: macOS 전용
- **입력**: YouTube URL만 (로컬 파일 미지원)
- **길이**: 최대 10분
- **캐싱**: 없음 (매번 새로 처리)
- **배치**: 없음 (단일 URL만)
- **웹 UI**: 없음 (CLI만)

### 기술적 제한

- `scipy < 1.15` 필수 (deprecated gaussian 함수 사용)
- LilyPond 미설치 시 PDF 생성 불가
- basic-pitch AI 정확도에 따른 품질 한계

## Dependencies

### Python Packages

```
yt-dlp
basic-pitch
music21
onnxruntime
scipy<1.15
librosa          # 오디오 전처리
soundfile        # 오디오 I/O
noisereduce      # 노이즈 제거
numpy
pretty_midi      # MIDI 처리
```

버전 고정 없이 유연하게 관리 (scipy만 예외)

### System Dependencies (macOS)

```bash
brew install ffmpeg lilypond
```

- FFmpeg: 필수 (오디오 변환)
- LilyPond: 선택 (PDF 렌더링)

## Future Plans

> 향후 개선 예정.

- ~~음질 전처리로 채보 품질 향상~~ ✅ 구현됨
- ~~basic-pitch 파라미터 최적화~~ ✅ 구현됨
- 조표/박자 자동 추정
- 소스 분리 (spleeter/demucs) - 혼합 오디오에서 피아노 분리
- 앙상블 모델 - 복수 모델 결합으로 정확도 향상

## File Structure

```
claude-plugins/
├── .claude-plugin/
│   └── plugin.json               # Claude 플러그인 설정
├── commands/
│   └── youtube-to-score.md       # /youtube-to-score 명령 정의
├── scripts/
│   └── setup.sh                  # 설치 스크립트
├── skills/youtube-to-score/
│   ├── SKILL.md                  # Claude 스킬 정의
│   └── scripts/
│       ├── main.py               # 파이프라인 통합 진입점
│       ├── downloader.py         # YouTube 오디오 추출
│       ├── transcriber.py        # AI MIDI 변환
│       └── renderer.py           # 악보 렌더링
├── downloads/                    # 다운로드된 WAV 파일
├── output/                       # 생성된 MIDI, XML, PDF
├── venv/                         # Python 가상환경
├── README.md                     # 사용자 가이드
├── SPEC.md                       # 이 문서
└── CLAUDE.md                     # Claude Code 가이드
```
