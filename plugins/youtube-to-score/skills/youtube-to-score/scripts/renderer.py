#!/usr/bin/env python3
"""악보 렌더링 모듈: MIDI → MusicXML, PDF 변환"""

import os
import tempfile
import shutil
import subprocess
from music21 import converter


def midi_to_score(midi_path, output_path):
    """MIDI 파일을 MusicXML과 PDF로 변환

    Args:
        midi_path: 입력 MIDI 파일 경로
        output_path: 출력 PDF 파일 경로

    Returns:
        tuple: (xml_path, pdf_path) - PDF 생성 실패 시 pdf_path는 None
    """
    print(f"{midi_path} → 악보 변환 중...")
    score = converter.parse(midi_path)

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
