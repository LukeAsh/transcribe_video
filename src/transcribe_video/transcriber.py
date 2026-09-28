"""Audio transcription using faster-whisper."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """Raised when transcription fails."""


def transcribe(
    audio_path: str | Path,
    model_size: str = "base",
    language: str | None = None,
    output_dir: str | Path | None = None,
    output_formats: list[str] | None = None,
    device: str | None = None,
) -> dict[str, Path]:
    """Transcribe an audio file using faster-whisper.

    Args:
        audio_path: Path to the audio file.
        model_size: Whisper model size (tiny, base, small, medium, large-v3).
        language: Language code (e.g., "en"). Auto-detected if None.
        output_dir: Directory for output files. Defaults to audio file's directory.
        output_formats: List of output formats (txt, srt, vtt). Defaults to ["txt"].
        device: Compute device ("cuda", "cpu", "auto"). Auto-detected if None.

    Returns:
        Dictionary mapping format name to output file path.

    Raises:
        TranscriptionError: If transcription fails.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise TranscriptionError(f"Audio file not found: {audio_path}")

    if output_dir is None:
        output_dir = audio_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    if output_formats is None:
        output_formats = ["txt"]

    if device is None:
        device = "auto"

    logger.info("Loading whisper model: %s (device=%s)", model_size, device)

    try:
        model = WhisperModel(model_size, device=device, compute_type="int8")
    except Exception as e:
        # Check if this is a CUDA-related error and we're not already on CPU
        error_msg = str(e).lower()
        is_cuda_error = any(
            keyword in error_msg
            for keyword in ["libcublas", "libcudart", "cuda", "cudnn", "libcurand", "libcusparse"]
        )
        if is_cuda_error and device != "cpu":
            logger.warning(
                "CUDA error detected (%s). Falling back to CPU. "
                "Install CUDA toolkit for GPU acceleration.",
                e,
            )
            device = "cpu"
            logger.info("Retrying with device=%s", device)
            try:
                model = WhisperModel(model_size, device=device, compute_type="int8")
            except Exception as e2:
                raise TranscriptionError(
                    f"Failed to load model '{model_size}' on CPU: {e2}"
                ) from e2
        else:
            raise TranscriptionError(f"Failed to load model '{model_size}': {e}") from e

    logger.info("Transcribing: %s", audio_path)

    try:
        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            vad_filter=True,
        )
    except Exception as e:
        raise TranscriptionError(f"Transcription failed: {e}") from e

    logger.info(
        "Detected language: %s (probability: %.2f)",
        info.language,
        info.language_probability,
    )

    # Collect all segments
    segment_list = list(segments)

    results: dict[str, Path] = {}
    base_name = audio_path.stem

    for fmt in output_formats:
        output_file = output_dir / f"{base_name}.{fmt}"

        if fmt == "txt":
            _write_txt(segment_list, output_file)
        elif fmt == "srt":
            _write_srt(segment_list, output_file)
        elif fmt == "vtt":
            _write_vtt(segment_list, output_file)
        else:
            logger.warning("Unsupported output format: %s", fmt)
            continue

        logger.info("Wrote %s: %s", fmt.upper(), output_file)
        results[fmt] = output_file

    return results


def _write_txt(segments: list[Any], output_file: Path) -> None:
    """Write plain text output."""
    with open(output_file, "w", encoding="utf-8") as f:
        for segment in segments:
            f.write(segment.text.strip())
            f.write("\n")


def _write_srt(segments: list[Any], output_file: Path) -> None:
    """Write SRT subtitle output."""
    with open(output_file, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(f"{_srt_time(segment.start)} --> {_srt_time(segment.end)}\n")
            f.write(f"{segment.text.strip()}\n\n")


def _write_vtt(segments: list[Any], output_file: Path) -> None:
    """Write WebVTT subtitle output."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for segment in segments:
            f.write(f"{_vtt_time(segment.start)} --> {_vtt_time(segment.end)}\n")
            f.write(f"{segment.text.strip()}\n\n")


def _srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _vtt_time(seconds: float) -> str:
    """Format seconds as WebVTT timestamp (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
