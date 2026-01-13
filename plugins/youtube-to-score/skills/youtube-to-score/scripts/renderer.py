#!/usr/bin/env python3
"""악보 렌더링 모듈: MIDI → MusicXML, PDF 변환

개선된 후처리 포함:
- MIDI 퀀타이즈 (타이밍 보정)
- 옥타브 오류 수정
- 피아노 범위 외 노트 필터링
"""

import os
import tempfile
import shutil
import subprocess
from music21 import converter, stream, note, chord, pitch


class MidiPostProcessConfig:
    """MIDI 후처리 설정"""
    # 퀀타이즈 설정
    QUANTIZE = True
    QUANTIZE_DIVISORS = [4, 3]    # 16분음표, 8분음표 셋잇단음표

    # 옥타브 오류 수정
    FIX_OCTAVE_ERRORS = True
    MAX_INTERVAL_SEMITONES = 12   # 연속 노트 간 최대 허용 간격

    # 피아노 범위 필터링
    FILTER_PIANO_RANGE = True
    PIANO_MIN_MIDI = 21           # A0 (MIDI 21)
    PIANO_MAX_MIDI = 108          # C8 (MIDI 108)

    # 짧은 노트 필터링
    FILTER_SHORT_NOTES = True
    MIN_DURATION_QUARTER = 0.125  # 32분음표 이하 필터링


def fix_octave_errors(score, config=None):
    """옥타브 오류 수정

    연속된 노트에서 비정상적인 옥타브 점프를 감지하고 수정합니다.
    """
    if config is None:
        config = MidiPostProcessConfig()

    print("  [후처리] 옥타브 오류 수정 중...")
    fixed_count = 0

    for part in score.parts:
        notes_list = list(part.flatten().notes)

        for i in range(1, len(notes_list)):
            prev_elem = notes_list[i - 1]
            curr_elem = notes_list[i]

            # chord인 경우 첫 번째 노트 사용
            prev_pitch = prev_elem.pitch if hasattr(prev_elem, 'pitch') else (
                prev_elem.pitches[0] if hasattr(prev_elem, 'pitches') and prev_elem.pitches else None
            )
            curr_pitch = curr_elem.pitch if hasattr(curr_elem, 'pitch') else (
                curr_elem.pitches[0] if hasattr(curr_elem, 'pitches') and curr_elem.pitches else None
            )

            if prev_pitch is None or curr_pitch is None:
                continue

            interval = abs(curr_pitch.midi - prev_pitch.midi)

            # 옥타브 이상 점프 감지 (멜로디 컨텍스트에서 비정상)
            if interval > config.MAX_INTERVAL_SEMITONES:
                # 가장 가까운 옥타브로 조정
                while abs(curr_pitch.midi - prev_pitch.midi) > config.MAX_INTERVAL_SEMITONES:
                    if curr_pitch.midi > prev_pitch.midi:
                        curr_pitch.octave -= 1
                    else:
                        curr_pitch.octave += 1
                    fixed_count += 1

    if fixed_count > 0:
        print(f"    → {fixed_count}개 옥타브 오류 수정됨")
    return score


def filter_piano_range(score, config=None):
    """피아노 범위 외 노트 필터링"""
    if config is None:
        config = MidiPostProcessConfig()

    print("  [후처리] 피아노 범위 필터링 중...")
    filtered_count = 0

    for part in score.parts:
        for elem in list(part.flatten().notes):
            pitches_to_check = []

            if hasattr(elem, 'pitch'):
                pitches_to_check = [elem.pitch]
            elif hasattr(elem, 'pitches'):
                pitches_to_check = list(elem.pitches)

            for p in pitches_to_check:
                if p.midi < config.PIANO_MIN_MIDI or p.midi > config.PIANO_MAX_MIDI:
                    # 범위 내로 옥타브 조정
                    while p.midi < config.PIANO_MIN_MIDI:
                        p.octave += 1
                        filtered_count += 1
                    while p.midi > config.PIANO_MAX_MIDI:
                        p.octave -= 1
                        filtered_count += 1

    if filtered_count > 0:
        print(f"    → {filtered_count}개 노트 피아노 범위로 조정됨")
    return score


def filter_short_notes(score, config=None):
    """너무 짧은 노트 필터링"""
    if config is None:
        config = MidiPostProcessConfig()

    print("  [후처리] 짧은 노트 필터링 중...")
    filtered_count = 0

    for part in score.parts:
        elements_to_remove = []
        for elem in part.flatten().notes:
            if elem.quarterLength < config.MIN_DURATION_QUARTER:
                elements_to_remove.append(elem)
                filtered_count += 1

        for elem in elements_to_remove:
            part.remove(elem, recurse=True)

    if filtered_count > 0:
        print(f"    → {filtered_count}개 짧은 노트 제거됨")
    return score


def postprocess_midi(score, config=None):
    """MIDI 후처리 파이프라인"""
    if config is None:
        config = MidiPostProcessConfig()

    print("[후처리] MIDI 품질 개선 중...")

    # 1. 퀀타이즈 (타이밍 보정)
    if config.QUANTIZE:
        print("  [후처리] 퀀타이즈 적용 중...")
        score.quantize(
            quarterLengthDivisors=config.QUANTIZE_DIVISORS,
            inPlace=True
        )
        print(f"    → 퀀타이즈 완료 (divisors: {config.QUANTIZE_DIVISORS})")

    # 2. 옥타브 오류 수정
    if config.FIX_OCTAVE_ERRORS:
        score = fix_octave_errors(score, config)

    # 3. 피아노 범위 필터링
    if config.FILTER_PIANO_RANGE:
        score = filter_piano_range(score, config)

    # 4. 짧은 노트 필터링
    if config.FILTER_SHORT_NOTES:
        score = filter_short_notes(score, config)

    return score


def midi_to_score(midi_path, output_path, config=None):
    """MIDI 파일을 MusicXML과 PDF로 변환 (후처리 포함)

    Args:
        midi_path: 입력 MIDI 파일 경로
        output_path: 출력 PDF 파일 경로
        config: MidiPostProcessConfig 인스턴스 (기본: None)

    Returns:
        tuple: (xml_path, pdf_path) - PDF 생성 실패 시 pdf_path는 None
    """
    if config is None:
        config = MidiPostProcessConfig()

    print(f"{midi_path} → 악보 변환 중...")
    score = converter.parse(midi_path)

    # MIDI 후처리 적용
    score = postprocess_midi(score, config)

    # MusicXML 저장
    xml_path = output_path.replace('.pdf', '.xml')
    score.write('musicxml', fp=xml_path)
    print(f"MusicXML 저장 완료: {xml_path}")

    pdf_path = None

    # PDF 렌더링 시도
    try:
        # 방법 1: music21 기본 렌더러 (MuseScore)
        score.write('musicxml.pdf', fp=output_path)
        print(f"PDF 저장 완료: {output_path}")
        pdf_path = output_path
    except Exception:
        print("기본 PDF 렌더링 실패, LilyPond 시도 중...")
        try:
            # 방법 2: LilyPond 직접 호출
            with tempfile.TemporaryDirectory() as tmp_dir:
                base_name = "score"
                ly_path = os.path.join(tmp_dir, f"{base_name}.ly")

                score.write('lilypond', fp=ly_path)

                subprocess.run(
                    ['lilypond', '--pdf', '-o', base_name, f"{base_name}.ly"],
                    cwd=tmp_dir,
                    check=True,
                    capture_output=True,
                    text=True
                )

                generated_pdf = os.path.join(tmp_dir, f"{base_name}.pdf")
                if os.path.exists(generated_pdf):
                    shutil.copy(generated_pdf, output_path)
                    print(f"PDF 저장 완료 (LilyPond): {output_path}")
                    pdf_path = output_path
                else:
                    raise FileNotFoundError("PDF 파일 생성 실패")

        except FileNotFoundError:
            print("\n[경고] PDF 생성 실패: LilyPond가 설치되어 있지 않습니다.")
            print("설치: brew install lilypond")
        except subprocess.CalledProcessError as e:
            print(f"\n[경고] PDF 생성 실패: {e.stderr}")
        except Exception as e:
            print(f"\n[경고] PDF 생성 실패: {e}")

    return xml_path, pdf_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("사용법: python renderer.py <midi_file> <output_pdf>")
    else:
        xml_file, pdf_file = midi_to_score(sys.argv[1], sys.argv[2])
        print(f"\n결과: XML={xml_file}, PDF={pdf_file}")
