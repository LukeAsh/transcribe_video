# transcribe-video

Download video and transcribe it using Whisper.

## Installation on Windows

```
winget install astral-sh.uv
winget install Microsoft.VCRedist.2015+.x64
winget install Gyan.FFmpeg
```

```bash
uv sync
```

## Usage

```bash
# Basic usage (auto-detect language, output .txt)
uv run transcribe-video <URL/FILE>

# Specify model and language
uv run transcribe-video <URL/FILE> --model small --language en

# Output subtitles too
uv run transcribe-video <URL/FILE> --output-format txt --output-format srt --output-format vtt

# Download/extract audio only instead of the full video
uv run transcribe-video <URL/FILE> --audio-only

# Verbose logging
uv run transcribe-video <URL/FILE> -v
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `base` | Whisper model: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `--language` | auto | Language code (e.g., `en`, `es`, `fr`) |
| `--output-format` | `txt` | Output format: `txt`, `srt`, `vtt` (repeatable) |
| `--audio-only` | off | Download only the audio track instead of the full video |
| `--output-dir` | `.` | Output directory |
| `--device` | auto | Compute device: `auto`, `cuda`, `cpu` |
| `--verbose` / `-v` | off | Enable verbose logging |

## Development

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy src/
```
