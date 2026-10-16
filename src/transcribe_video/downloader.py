"""Video/audio downloader using yt-dlp."""

from __future__ import annotations

import logging
from pathlib import Path

import yt_dlp  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Raised when a download fails."""


def download_media(
    url: str,
    output_dir: str | Path = ".",
    audio_only: bool = False,
    audio_format: str = "mp3",
    cookies: str | None = None,
    cookies_from_browser: str | None = None,
    player_client: str | None = None,
    js_runtimes: list[str] | None = None,
    remote_components: list[str] | None = None,
) -> Path:
    """Download a video, or just its audio track, from a URL.

    Args:
        url: The video URL (YouTube, etc.).
        output_dir: Directory to save the downloaded file.
        audio_only: If True, download only the audio track. If False,
            download the best video with audio.
        audio_format: Audio format to extract when audio_only is True
            (mp3, wav, etc.).
        cookies: Path to a Netscape cookies file (e.g. cookies.txt) for
            authenticated downloads.
        cookies_from_browser: Browser to load cookies from (e.g. chrome, firefox,
            edge) for authenticated downloads.
        player_client: YouTube player client(s), e.g. "default,web_embedded".
        js_runtimes: JavaScript runtimes for challenge solving, e.g. ["deno"]
            or ["node:/path/to/node"].
        remote_components: Remote components to allow, e.g. ["ejs:github"].

    Returns:
        Path to the downloaded file.

    Raises:
        DownloadError: If the download fails.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template = str(output_dir / "%(title)s.%(ext)s")

    ydl_opts: dict[str, object] = {
        "outtmpl": template,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # Sanitize filenames to handle special characters
        "restrictfilenames": False,
        "windowsfilenames": True,
    }

    if audio_only:
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "192",
            }
        ]
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"
        ydl_opts["merge_output_format"] = "mp4"

    if cookies:
        ydl_opts["cookiefile"] = cookies
    if cookies_from_browser:
        # yt-dlp expects a tuple (browser, profile, keyring, container);
        # a plain string would be unpacked character by character.
        ydl_opts["cookiesfrombrowser"] = tuple(cookies_from_browser.split(":"))
    if player_client:
        # extractor_args values must be lists of strings, not a single string.
        ydl_opts["extractor_args"] = {
            "youtube": {"player_client": [c for c in player_client.split(",") if c]}
        }
    if js_runtimes:
        # yt-dlp expects {runtime: {"path": path | None}}.
        runtimes: dict[str, dict[str, str | None]] = {}
        for arg in js_runtimes:
            runtime, _, path = arg.partition(":")
            runtimes[runtime.lower()] = {"path": path or None}
        ydl_opts["js_runtimes"] = runtimes
    if remote_components:
        ydl_opts["remote_components"] = remote_components

    logger.info("Downloading %s from: %s", "audio" if audio_only else "video", url)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise DownloadError(f"Could not extract info from: {url}")

            # Use yt-dlp's prepare_filename to get the actual saved filename
            # This handles all special character sanitization correctly
            actual_filename = ydl.prepare_filename(info)
            if audio_only:
                # Replace the extension with our audio format
                actual_path = Path(actual_filename).with_suffix(f".{audio_format}")
            else:
                actual_path = Path(actual_filename)

            if not actual_path.exists():
                raise DownloadError(f"Download completed but file not found: {actual_path}")

            logger.info("Downloaded: %s", actual_path)
            return actual_path

    except yt_dlp.utils.DownloadError as e:
        raise DownloadError(f"Failed to download {url}: {e}") from e
