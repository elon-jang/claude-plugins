# Development Plan & Progress

## Completed Phases

### Phase 1: Setup & Prototypes

- [x] Create virtual environment and install core dependencies.
- [x] Implement YouTube audio downloader using `yt-dlp`.
- [x] Implement basic AI transcription using `basic-pitch`.
- [x] Implement MusicXML output using `music21`.

### Phase 2: Integration & Bug Fixing

- [x] **Integrated Pipeline**: Created `main.py` to automate the whole process.
- [x] **Playlist Handling**: Fixed issue where `yt-dlp` would download whole playlists instead of single videos.
- [x] **Backend Compatibility**: Switched to ONNX backend for `basic-pitch` to solve model loading errors on Mac.
- [x] **Library Patches**: Applied monkey-patch for `scipy.signal.gaussian` removed in SciPy 1.17.

### Phase 3: Final Output & PDF Rendering

- [x] **PDF Support**: Integrated `LilyPond` as the default PDF renderer.
- [x] **Corruption Fix**: Resolved issue where PDF files were being saved as text source instead of binaries.
- [x] **Filename Sanitization**: Implemented temporary safe-naming to prevent character-level path errors during rendering.

## Future Plans (Optional)

- **Source Separation**: Add `demucs` to isolate piano/vocals before transcription.
- **Web UI**: Create a Streamlit interface for non-technical users.
- **Format Conversion**: Support more output formats like MIDI individual tracks.
