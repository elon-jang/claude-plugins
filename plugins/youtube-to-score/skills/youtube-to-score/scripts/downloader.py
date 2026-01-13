#!/usr/bin/env python3
"""YouTube 오디오 다운로더: YouTube URL에서 WAV 추출"""

import os
import yt_dlp

MAX_DURATION_SECONDS = 600  # 10분


class DownloadError(Exception):
    """다운로드 관련 오류"""
    pass


def _get_korean_error_message(error_str):
    """yt-dlp 오류를 한글 메시지로 변환"""
    error_lower = error_str.lower()

    if 'copyright' in error_lower or 'blocked' in error_lower:
        return "이 영상은 저작권으로 인해 다운로드할 수 없습니다."
    elif 'not available' in error_lower or 'unavailable' in error_lower:
        return "이 영상은 현재 지역에서 이용할 수 없습니다."
    elif 'private' in error_lower:
        return "이 영상은 비공개 상태입니다."
    elif 'removed' in error_lower or 'deleted' in error_lower:
        return "이 영상은 삭제되었습니다."
    elif 'url' in error_lower or 'invalid' in error_lower or 'not a valid' in error_lower:
        return "올바른 YouTube URL을 입력해주세요."
    elif 'network' in error_lower or 'connection' in error_lower or 'timed out' in error_lower:
        return "네트워크 연결을 확인해주세요."
    elif 'age' in error_lower or 'sign in' in error_lower:
        return "이 영상은 로그인이 필요하거나 연령 제한이 있습니다."
    else:
        return f"다운로드 중 오류가 발생했습니다: {error_str}"


def download_audio(youtube_url, output_dir='downloads'):
    """YouTube URL에서 오디오를 WAV로 다운로드

    Args:
        youtube_url: YouTube 영상 URL
        output_dir: 출력 디렉토리 (기본: downloads/)

    Returns:
        tuple: (파일경로, 10분_초과_여부)

    Raises:
        DownloadError: 다운로드 실패 시
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 공통 옵션 (경고 억제)
    base_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }

    # 먼저 영상 정보를 가져와서 길이 확인
    try:
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
    except Exception as e:
        raise DownloadError(_get_korean_error_message(str(e)))

    duration = info.get('duration', 0)
    is_trimmed = False

    if duration > MAX_DURATION_SECONDS:
        print(f"영상 길이: {duration // 60}분 {duration % 60}초")
        print(f"최대 {MAX_DURATION_SECONDS // 60}분까지 처리. 첫 10분만 추출합니다.")
        is_trimmed = True

    # 다운로드 옵션
    ydl_opts = {
        **base_opts,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
    }

    # 10분 초과 시 첫 10분만 다운로드
    if is_trimmed:
        ydl_opts['download_ranges'] = lambda info, ydl: [{'start_time': 0, 'end_time': MAX_DURATION_SECONDS}]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
            filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.wav'
            return filename, is_trimmed
    except Exception as e:
        raise DownloadError(_get_korean_error_message(str(e)))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("사용법: python downloader.py <youtube_url>")
    else:
        url = sys.argv[1]
        print(f"다운로드 중: {url}")
        try:
            file_path, trimmed = download_audio(url)
            print(f"완료: {file_path}")
            if trimmed:
                print("(첫 10분만 추출됨)")
        except DownloadError as e:
            print(f"오류: {e}")
