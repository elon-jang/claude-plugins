import os
import sys
from downloader import download_audio, DownloadError
from transcriber import transcribe_audio_to_midi
from renderer import midi_to_score

def run_pipeline(youtube_url):
    print("=== 1단계: 오디오 다운로드 ===")
    try:
        audio_file, is_trimmed = download_audio(youtube_url)
    except DownloadError as e:
        print(f"오류: {e}")
        sys.exit(1)

    print(f"오디오 다운로드 완료: {audio_file}")
    if is_trimmed:
        print("(첫 10분만 추출됨)")

    print("\n=== 2단계: MIDI 변환 ===")
    midi_file = transcribe_audio_to_midi(audio_file)
    print(f"MIDI 생성 완료: {midi_file}")

    print("\n=== 3단계: 악보 렌더링 ===")
    output_pdf = midi_file.replace('.mid', '.pdf')
    midi_to_score(midi_file, output_pdf)

    print("\n=== 변환 완료 ===")
    print(f"최종 악보: {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python main.py <youtube_url>")
    else:
        url = sys.argv[1]
        run_pipeline(url)
