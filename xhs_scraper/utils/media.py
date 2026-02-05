"""Async media download utility for images and videos."""

import asyncio
import logging
import re
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


async def download_media(
    urls: list[str],
    output_dir: str | Path,
    filename_pattern: str = "{index}.{ext}",
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
    note_id: Optional[str] = None,
) -> list[Path]:
    """Download media files from URLs asynchronously.

    Args:
        urls: List of media URLs to download
        output_dir: Directory to save downloaded files
        filename_pattern: Pattern for filenames, supports {index}, {ext}, {note_id}
        progress_callback: Optional async callback for progress updates (url, bytes_downloaded, total_bytes)
        note_id: Optional note ID for use in filename pattern

    Returns:
        List of Path objects for successfully downloaded files

    Example:
        >>> urls = ["https://example.com/img1.jpg", "https://example.com/img2.png"]
        >>> paths = await download_media(urls, "./media", "{note_id}_{index}.{ext}", note_id="note123")
        >>> print(paths)
        [PosixPath("./media/note123_0.jpg"), PosixPath("./media/note123_1.png")]
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    downloaded_paths: list[Path] = []

    # Create tasks for all downloads
    tasks = []
    for index, url in enumerate(urls):
        task = _download_single_media(
            url,
            output_dir,
            index,
            filename_pattern,
            progress_callback,
            note_id,
        )
        tasks.append(task)

    # Run all downloads concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect successful downloads
    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"Media download failed: {result}")
        elif result is not None:
            downloaded_paths.append(result)

    return downloaded_paths


async def _download_single_media(
    url: str,
    output_dir: Path,
    index: int,
    filename_pattern: str,
    progress_callback: Optional[Callable[[str, int, int], None]],
    note_id: Optional[str],
) -> Optional[Path]:
    """Download a single media file.

    Args:
        url: URL to download
        output_dir: Directory to save file
        index: Index of file in batch
        filename_pattern: Filename pattern
        progress_callback: Optional progress callback
        note_id: Optional note ID

    Returns:
        Path to downloaded file or None if failed
    """
    try:
        # Extract extension from URL or determine from Content-Type
        ext = _extract_extension(url)

        # Format filename
        filename = filename_pattern.format(
            index=index,
            ext=ext,
            note_id=note_id or "",
        )
        # Clean up filename if note_id was empty
        filename = filename.replace("__", "_").replace("_.", ".")

        filepath = output_dir / filename

        # Download with streaming
        async with httpx.AsyncClient(follow_redirects=True) as client:
            async with client.stream("GET", url, timeout=30.0) as response:
                response.raise_for_status()

                # Get total content length for progress tracking
                total_bytes = int(response.headers.get("content-length", 0))
                downloaded_bytes = 0

                # Write to file with progress updates
                with open(filepath, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_bytes += len(chunk)

                            if progress_callback:
                                await progress_callback(
                                    url, downloaded_bytes, total_bytes
                                )

        logger.info(f"Downloaded media: {url} -> {filepath}")
        return filepath

    except httpx.RequestError as e:
        logger.warning(f"Request error downloading {url}: {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error downloading {url}: {e.response.status_code}")
        return None
    except IOError as e:
        logger.warning(f"IO error saving media from {url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error downloading {url}: {e}")
        return None


def _extract_extension(url: str) -> str:
    """Extract file extension from URL.

    Args:
        url: URL to extract extension from

    Returns:
        File extension without dot (e.g., 'jpg', 'mp4')
    """
    # Parse URL to get path
    parsed = urlparse(url)
    path = parsed.path

    # Extract extension from path
    match = re.search(r"\.([a-zA-Z0-9]+)(?:\?|$)", path)
    if match:
        ext = match.group(1).lower()
        # Handle common variations
        if ext in ("jpeg",):
            return "jpg"
        return ext

    # Fallback to common extensions based on typical patterns
    # This is a reasonable default for unknown types
    return "bin"
