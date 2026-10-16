# transcribe-video

Download video audio and transcribe it using Whisper.

## Installation

```bash
uv sync
```

## Usage

```bash
# Basic usage (auto-detect language, output .txt)
uv run transcribe-video <URL>

# Specify model and language
uv run transcribe-video <URL> --model small --language en

# Output subtitles too
uv run transcribe-video <URL> --output-format txt --output-format srt --output-format vtt

# Download audio only instead of the full video
uv run transcribe-video <URL> --audio-only

# Verbose logging
uv run transcribe-video <URL> -v
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
