"""Video/audio downloader using yt-dlp."""

from __future__ import annotations

import logging
from pathlib import Path

import yt_dlp  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Raised when a download fails."""


def download_audio(
    url: str,
    output_dir: str | Path = ".",
    audio_format: str = "mp3",
    cookies: str | None = None,
    cookies_from_browser: str | None = None,
    player_client: str | None = None,
    js_runtimes: str | None = None,
    remote_components: str | None = None,
) -> Path:
    """Download the audio track from a video URL.

    Args:
        url: The video URL (YouTube, etc.).
        output_dir: Directory to save the audio file.
        audio_format: Audio format to extract (mp3, wav, etc.).
        cookies: Path to a Netscape cookies file (e.g. cookies.txt) for
            authenticated downloads.
        cookies_from_browser: Browser to load cookies from (e.g. chrome, firefox,
            edge) for authenticated downloads.
        player_client: YouTube player client(s), e.g. "default,web_embedded".
        js_runtimes: JavaScript runtime for challenge solving, e.g. "deno",
            "node", or "deno:/path/to/deno".
        remote_components: Remote components to allow, e.g. "ejs:github".

    Returns:
        Path to the downloaded audio file.

    Raises:
        DownloadError: If the download fails.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template = str(output_dir / "%(title)s.%(ext)s")

    ydl_opts: dict[str, object] = {
        "format": "bestaudio/best",
        "outtmpl": template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # Sanitize filenames to handle special characters
        "restrictfilenames": False,
        "windowsfilenames": True,
    }

    if cookies:
        ydl_opts["cookiefile"] = cookies
    if cookies_from_browser:
        # yt-dlp expects a tuple (browser, profile, keyring, container);
        # a plain string would be unpacked character by character.
        ydl_opts["cookiesfrombrowser"] = tuple(cookies_from_browser.split(":"))

    logger.info("Downloading audio from: %s", url)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise DownloadError(f"Could not extract info from: {url}")

            # Use yt-dlp's prepare_filename to get the actual saved filename
            # This handles all special character sanitization correctly
            actual_filename = ydl.prepare_filename(info)
            # Replace the extension with our audio format
            actual_path = Path(actual_filename).with_suffix(f".{audio_format}")

            if not actual_path.exists():
                raise DownloadError(f"Download completed but file not found: {actual_path}")

            logger.info("Downloaded: %s", actual_path)
            return actual_path

    except yt_dlp.utils.DownloadError as e:
        raise DownloadError(f"Failed to download {url}: {e}") from e
