"""Command-line interface for transcribe-video."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from transcribe_video.downloader import DownloadError, download_audio
from transcribe_video.transcriber import TranscriptionError, transcribe


def main() -> None:
    """Entry point for the transcribe-video CLI."""
    parser = argparse.ArgumentParser(
        prog="transcribe-video",
        description="Download video audio and transcribe it using Whisper.",
    )
    parser.add_argument("url", help="Video URL to download and transcribe")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Language code (e.g., en, es). Auto-detected if not specified.",
    )
    parser.add_argument(
        "--output-format",
        action="append",
        dest="output_formats",
        choices=["txt", "srt", "vtt"],
        help="Output format(s). Can be specified multiple times. Default: txt",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Defaults to current directory.",
    )
    parser.add_argument(
        "--device",
        default=None,
        choices=["auto", "cuda", "cpu"],
        help="Compute device. Auto-detected if not specified.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging.",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    output_formats = args.output_formats or ["txt"]
    output_dir = Path(args.output_dir) if args.output_dir else Path(".")

    # Step 1: Download audio
    try:
        audio_path = download_audio(args.url, output_dir=output_dir)
    except DownloadError as e:
        logging.error("Download failed: %s", e)
        sys.exit(1)

    # Step 2: Transcribe
    try:
        results = transcribe(
            audio_path=audio_path,
            model_size=args.model,
            language=args.language,
            output_dir=output_dir,
            output_formats=output_formats,
            device=args.device,
        )
    except TranscriptionError as e:
        logging.error("Transcription failed: %s", e)
        sys.exit(1)

    # Summary
    print("\n--- Transcription complete ---")
    for fmt, path in results.items():
        print(f"  {fmt.upper()}: {path}")


if __name__ == "__main__":
    main()
