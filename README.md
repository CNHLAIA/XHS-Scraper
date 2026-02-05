# xhs-scraper - Async Xiaohongshu (RED) Scraper

An efficient async Python library for scraping Xiaohongshu (小红书/RED) data, supporting notes, users, comments, and search functionality.

**[English](./README.md)** | **[中文文档](./docs/README_CN.md)**

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Cookie Setup](#cookie-setup)
- [API Reference](#api-reference)
- [Data Models](#data-models)
- [Data Export](#data-export)
- [Media Download](#media-download)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)
- [FAQ](#faq)
- [Disclaimer](#disclaimer)

## Features

- **Note Scraping**: Collect detailed information from image and video notes.
- **User Scraping**: Retrieve user profile information, followers, and following counts.
- **Comment Scraping**: Support for nested comments with pagination.
- **Keyword Search**: Search with sorting options (general, latest, popular) and note type filters (all, video, image).
- **Media Download**: Download HD images and watermark-free videos.
- **Data Export**: Built-in JSON and CSV export utilities.
- **Async Support**: Fully asynchronous implementation based on `httpx` for high performance.
- **Rate Control**: Built-in token bucket rate limiter to protect your account.

## Requirements

- Python >= 3.10
- Core dependencies:
  - `httpx`: Async HTTP client
  - `xhshow`: Xiaohongshu signature tool
  - `pydantic`: Data modeling and validation
  - `tenacity`: Retry mechanism

## Installation

Install in development mode:

```bash
git clone https://github.com/your-username/xhs-scraper.git
cd xhs-scraper
pip install -e .
```

## Quick Start

Here's a simple example showing how to initialize the client and fetch user information:

```python
import asyncio
from xhs_scraper import XHSClient

async def main():
    # Enter your cookies
    cookies = {
        "a1": "your_a1_value",
        "web_session": "your_web_session_value"
    }
    
    # Initialize client using async context manager
    async with XHSClient(cookies=cookies, rate_limit=2.0) as client:
        # Get user information
        user = await client.users.get_user_info("user_id")
        print(f"Nickname: {user.nickname}")
        print(f"Followers: {user.followers}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Cookie Setup

This tool supports multiple methods to obtain cookies:

### Method 1: Browser DevTools
1. Open Xiaohongshu in your browser and log in.
2. Press `F12` to open DevTools, go to the `Network` tab.
3. Refresh the page, click on any request, and copy the `Cookie` field from `Request Headers`.
4. Extract key fields like `a1` and `web_session`.

### Method 2: Chrome Auto-Extraction
If you're logged into Xiaohongshu in Chrome, you can automatically extract cookies:

```python
from xhs_scraper.utils import extract_chrome_cookies

cookies = extract_chrome_cookies()
# The returned cookies can be passed directly to XHSClient
```

### Method 3: QR Code Login
Log in by scanning a QR code:

```python
from xhs_scraper import qr_login

async def login():
    cookies = await qr_login()
    print(f"Obtained cookies: {cookies}")
```

## API Reference

### XHSClient
The main entry point that coordinates all scraper modules.

- **Initialization Parameters**:
  - `cookies`: (dict) Xiaohongshu cookie dictionary.
  - `rate_limit`: (float) Maximum requests per second, default 2.0.
  - `timeout`: (float) Request timeout in seconds.

- **Properties**:
  - `notes`: `NoteScraper` instance
  - `users`: `UserScraper` instance
  - `comments`: `CommentScraper` instance
  - `search`: `SearchScraper` instance

### NoteScraper
For fetching note details or user's posted notes.

- `get_note(note_id, xsec_token) -> NoteResponse`
  - Get details of a single note.
- `get_user_notes(user_id, cursor="", max_pages=1) -> PaginatedResponse[NoteResponse]`
  - Get notes posted by a specific user.

### UserScraper
For fetching user information.

- `get_user_info(user_id) -> UserResponse`
  - Get another user's profile information.
- `get_self_info() -> UserResponse`
  - Get the current logged-in user's information.

### CommentScraper
For fetching comments on notes.

- `get_comments(note_id, cursor="", max_pages=1) -> PaginatedResponse[CommentResponse]`
  - Get top-level comments on a note.
- `get_sub_comments(note_id, root_comment_id, cursor="") -> PaginatedResponse[CommentResponse]`
  - Get replies to a specific comment.

### SearchScraper
Search for notes by keyword.

- `search_notes(keyword, page=1, page_size=20, sort="GENERAL", note_type="ALL") -> SearchResultResponse`
  - `sort` options: `"GENERAL"` (default), `"TIME_DESC"` (latest), `"POPULARITY"` (popular)
  - `note_type` options: `"ALL"` (default), `"VIDEO"`, `"IMAGE"`

## Data Models

This project uses Pydantic for data validation. Main models:

### UserResponse
- `user_id`: Unique user identifier
- `nickname`: Display name
- `avatar`: Avatar URL
- `bio`: User bio
- `followers`: Follower count
- `following`: Following count

### NoteResponse
- `note_id`: Note ID
- `title`: Title
- `desc`: Content/description
- `images`: List of image URLs
- `video`: Video info (for video notes)
- `user`: Author info (`UserResponse`)
- `liked_count`: Like count
- `commented_count`: Comment count
- `shared_count`: Share count

### CommentResponse
- `comment_id`: Comment ID
- `content`: Comment text
- `user`: Commenter info
- `create_time`: Timestamp
- `sub_comments`: List of replies

## Data Export

### JSON Export
```python
from xhs_scraper.utils import export_to_json

# data can be a model list or PaginatedResponse object
export_to_json(notes, "output/notes.json")
```

### CSV Export
```python
from xhs_scraper.utils import export_to_csv

export_to_csv(notes, "output/notes.csv")
```

## Media Download

Download media resources associated with notes:

```python
from xhs_scraper.media import download_media

# Automatically detect and download images or videos
await download_media(note, folder="downloads/")
```

## Error Handling

The library defines a detailed exception hierarchy:

| Exception | Description | HTTP Status |
|-----------|-------------|-------------|
| `XHSError` | Base class for all custom exceptions | - |
| `SignatureError` | API signature validation failed | 461 |
| `CaptchaRequiredError` | Captcha verification required | 471 |
| `CookieExpiredError` | Cookie expired or not logged in | 401 / 403 |
| `RateLimitError` | Too many requests | 429 |
| `APIError` | General API error | - |

## Rate Limiting

This project includes a built-in token bucket rate limiter.

- **Configuration**: Control via `rate_limit` parameter when initializing `XHSClient` (unit: requests/second).
- **Purpose**: Automatically smooths request frequency to prevent being blocked by Xiaohongshu servers.

## Examples

### Example 1: Scrape User's Notes
```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_json

async def run():
    async with XHSClient(cookies={"a1": "...", "web_session": "..."}) as client:
        # Scrape first 3 pages of notes
        result = await client.notes.get_user_notes("user_id", max_pages=3)
        export_to_json(result.items, "user_notes.json")

asyncio.run(run())
```

### Example 2: Search and Export Notes
```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_csv

async def run():
    async with XHSClient(cookies={...}) as client:
        # Search "camping gear", sort by popularity
        search_res = await client.search.search_notes("camping gear", sort="POPULARITY")
        export_to_csv(search_res.items, "search_result.csv")

asyncio.run(run())
```

### Example 3: Scrape Note Comments
```python
import asyncio
from xhs_scraper import XHSClient

async def run():
    async with XHSClient(cookies={...}) as client:
        note_id = "65xxxxxxxxxxxxxxxx"
        comments = await client.comments.get_comments(note_id, max_pages=2)
        for comment in comments.items:
            print(f"{comment.user.nickname}: {comment.content}")

asyncio.run(run())
```

## FAQ

**Q: How do I get xsec_token?**
A: The `xsec_token` is typically found in note share links or in the data packets from homepage listings. When using this library, notes obtained through search or user listings usually already contain this token.

**Q: How long do cookies last?**
A: Generally, `web_session` has a shorter validity period (days to weeks), while `a1` lasts longer. It's recommended to check regularly or re-login via QR code.

**Q: How to avoid getting banned?**
A: 
1. Lower `rate_limit` (recommended 1.0 - 2.0).
2. Avoid long-duration, high-intensity scraping.
3. If you encounter a 471 error, stop immediately and complete verification manually in the browser.

## Disclaimer

- **Legal Use**: This tool is for learning and research purposes only. Please comply with Xiaohongshu's Terms of Service and applicable laws.
- **Responsible Scraping**: Respect the target platform's server load. Do not perform destructive data collection.
- **Privacy Protection**: Do not leak any personal privacy data obtained.
- **No Liability**: The author is not responsible for account bans or other legal consequences resulting from misuse of this tool.

## License

MIT License
