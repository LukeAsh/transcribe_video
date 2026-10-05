"""Command-line interface for transcribe-video."""

from __future__ import annotations

import argparse
import logging
import logging.config
import sys
from pathlib import Path

from transcribe_video.downloader import DownloadError, download_audio
from transcribe_video.transcriber import TranscriptionError, transcribe

LOG_FILE = Path("transcribe_video.log")

LOGGING_CONFIG: dict[str, object] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(LOG_FILE),
            "mode": "a",
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    },
}


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
        "--cookies",
        default=None,
        help="Path to a Netscape cookies file (e.g. cookies.txt) for authenticated downloads",
    )
    parser.add_argument(
        "--cookies-from-browser",
        default=None,
        choices=[
            "brave",
            "chrome",
            "chromium",
            "edge",
            "firefox",
            "opera",
            "safari",
            "vivaldi",
            "whale",
        ],
        help=(
            "Load cookies from a browser for authenticated downloads. "
            "Optionally append :profile, :keyring or :container "
            "(e.g. firefox, chrome:default, vivaldi:default:BASICTEXT)"
        ),
    )
    parser.add_argument(
        "--player-client",
        default=None,
        help=(
            "YouTube player client(s) to use, e.g. default,web_embedded or web_safari. "
            "Useful when downloads fail with 'The page needs to be reloaded'"
        ),
    )
    parser.add_argument(
        "--js-runtimes",
        action="append",
        default=None,
        metavar="RUNTIME[:PATH]",
        help=(
            "JavaScript runtime for YouTube challenge solving, e.g. deno or "
            "node:/path/to/node. Can be specified multiple times."
        ),
    )
    parser.add_argument(
        "--remote-components",
        action="append",
        default=None,
        metavar="COMPONENT",
        help=(
            "Remote components to allow, e.g. ejs:github or ejs:npm. "
            "Can be specified multiple times."
        ),
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging.",
    )

    args = parser.parse_args()

    # Configure logging with dictConfig
    logging.config.dictConfig(LOGGING_CONFIG)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)
    logger.info("Logging to file: %s", LOG_FILE)

    output_formats = args.output_formats or ["txt"]
    output_dir = Path(args.output_dir) if args.output_dir else Path(".")

    # Step 1: Download audio
    try:
        audio_path = download_audio(
            args.url,
            output_dir=output_dir,
            cookies=args.cookies,
            cookies_from_browser=args.cookies_from_browser,
            player_client=args.player_client,
            js_runtimes=args.js_runtimes,
            remote_components=args.remote_components,
        )
    except DownloadError as e:
        logger.error("Download failed: %s", e)
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
        logger.error("Transcription failed: %s", e)
        sys.exit(1)

    # Summary
    print("\n--- Transcription complete ---")
    for fmt, path in results.items():
        print(f"  {fmt.upper()}: {path}")


if __name__ == "__main__":
    main()
