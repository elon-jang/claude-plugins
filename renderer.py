from music21 import converter, environment
import os

def midi_to_score(midi_path, output_path):
    print(f"{midi_path} → 악보 변환 중...")
    score = converter.parse(midi_path)

    # MusicXML 저장
    xml_path = output_path.replace('.pdf', '.xml')
    score.write('musicxml', fp=xml_path)
    print(f"MusicXML 저장 완료: {xml_path}")

    # PDF 렌더링 시도
    try:
        # 방법 1: music21 기본 렌더러 (MuseScore)
        score.write('musicxml.pdf', fp=output_path)
        print(f"PDF 저장 완료: {output_path}")
    except Exception as e:
        print(f"기본 PDF 렌더링 실패, LilyPond 시도 중...")
        try:
            # 방법 2: LilyPond 직접 호출
            import tempfile
            import shutil
            import subprocess

            with tempfile.TemporaryDirectory() as tmp_dir:
                base_name = "score"
                ly_path = os.path.join(tmp_dir, f"{base_name}.ly")

                score.write('lilypond', fp=ly_path)

                try:
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
                    else:
                        raise Exception("LilyPond 실행은 성공했으나 PDF 파일을 찾을 수 없습니다.")
                except subprocess.CalledProcessError as spe:
                    raise Exception(spe.stderr)
        except FileNotFoundError:
            print("\n[경고] PDF 생성 실패: LilyPond가 설치되어 있지 않습니다.")
            print("PDF 생성을 위해 LilyPond 설치를 권장합니다: brew install lilypond")
            print("MIDI와 MusicXML 파일은 정상적으로 생성되었습니다.")
        except Exception as ly_e:
            print(f"\n[경고] PDF 생성 실패: {ly_e}")
            print("PDF 생성을 위해 LilyPond 설치를 권장합니다: brew install lilypond")
            print("MIDI와 MusicXML 파일은 정상적으로 생성되었습니다.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("사용법: python renderer.py <midi_file_path> <output_pdf_path>")
    else:
        midi_to_score(sys.argv[1], sys.argv[2])
