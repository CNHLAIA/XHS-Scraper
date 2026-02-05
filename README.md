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

### Step 1: Download the Project

**Option A: Using Git (Recommended)**

1. **Open your terminal**:
   - **Windows**: Press `Win + R`, type `cmd`, press Enter
   - **Mac**: Open Launchpad → Search "Terminal" → Open it
   - **Linux**: Open your terminal emulator (Ctrl+Alt+T on Ubuntu)

2. **Run these commands**:
```bash
git clone https://github.com/CNHLAIA/XHS-Scraper.git
cd XHS-Scraper
```

**Option B: Download ZIP**

1. Open your browser and go to https://github.com/CNHLAIA/XHS-Scraper
2. Click the green **Code** button
3. Select **Download ZIP**
4. Extract to your desired location (e.g., Desktop)

### Step 2: Install Dependencies

Open terminal in the project directory and run:
```bash
pip install -e .
```

> 💡 **Tip**: If `pip` is not found, please install Python 3.10 or higher first

## Quick Start

Follow these steps to run your first scraper script in 5 minutes!

### Step 1: Create a Script File

1. **Open the project folder**
   - Navigate to the `XHS-Scraper` folder you downloaded
   - Open it

2. **Create a new file**
   - Right-click in empty space → New → Text Document
   - Rename it to `my_first_scraper.py` (make sure to remove `.txt`)
   - Or use VS Code, PyCharm, or any code editor to create it

3. **Open the file and paste the code**
   - Open `my_first_scraper.py`
   - Copy and paste the following code:

```python
# my_first_scraper.py
# This is your first Xiaohongshu scraper script!

import asyncio
from xhs_scraper import XHSClient

async def main():
    # ⬇️ Replace these with your own Cookie values (see Cookie Setup above)
    cookies = {
        "a1": "paste_your_a1_value_here",
        "web_session": "paste_your_web_session_value_here"
    }
    
    async with XHSClient(cookies=cookies, rate_limit=2.0) as client:
        # Get your own user info to verify Cookie is working
        user = await client.users.get_self_info()
        print("🎉 Login successful!")
        print(f"Your nickname: {user.nickname}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 2: Run the Script

1. **Open terminal in project folder**
   - Windows: Hold `Shift`, right-click in folder → "Open command window here" or "Open in Terminal"
   - Mac/Linux: Right-click → "Open Terminal Here" or use `cd` command
   
2. **Run the command**
```bash
python my_first_scraper.py
```

3. **Check the result**
   - If you see `🎉 Login successful!` and your nickname, everything works!
   - If there's an error, double-check your Cookie values

## Cookie Setup

### Method 1: Browser DevTools (Easiest - Recommended for Beginners)

**Step-by-step guide:**

**Step 1: Open Xiaohongshu Website**
- Open your browser (Chrome, Edge, or Firefox)
- Go to: `https://www.xiaohongshu.com`
- Log in to your Xiaohongshu account

**Step 2: Open Developer Tools**
- Press `F12` on your keyboard
- Or: Right-click anywhere on the page → Select "Inspect"
- A new panel will appear on the right or bottom of your screen

**Step 3: Switch to Network Tab**
- Find the `Network` tab at the top of DevTools and click it
- If you can't see it, click `>>` or `...` to expand more tabs

**Step 4: Refresh the Page**
- Press `F5` or click the browser's refresh button
- You'll see many requests appear in the Network panel

**Step 5: Find the Cookie**
- Click on any request in the list (the first one is fine)
- In the right panel, find the `Headers` tab
- Scroll down to find `Request Headers` section
- Look for the `Cookie:` line - it has a very long value
- Double-click to select the entire value, then `Ctrl+C` to copy

**Step 6: Extract Key Fields**
- In the copied content, find these two values:
  - `a1=xxxxxxxxx` (the content after a1=)
  - `web_session=xxxxxxxxx` (the content after web_session=)
- Save these two values - you'll need them later

> ⚠️ **Security Warning**: Cookies contain your login credentials. **NEVER share them with anyone!**

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

1. **Create file**: `scrape_user_notes.py`
2. **Paste code**:
```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_json

async def run():
    # Replace with your own cookies
    cookies = {"a1": "...", "web_session": "..."}
    async with XHSClient(cookies=cookies) as client:
        # Scrape first 3 pages of notes
        result = await client.notes.get_user_notes("user_id", max_pages=3)
        export_to_json(result.items, "user_notes.json")

if __name__ == "__main__":
    asyncio.run(run())
```
3. **Run**: `python scrape_user_notes.py`
4. **Output location**: `user_notes.json`

### Example 2: Search and Export Notes

1. **Create file**: `search_and_export.py`
2. **Paste code**:
```python
import asyncio
from xhs_scraper import XHSClient
from xhs_scraper.utils import export_to_csv

async def run():
    # Replace with your own cookies
    cookies = {"a1": "...", "web_session": "..."}
    async with XHSClient(cookies=cookies) as client:
        # Search "camping gear", sort by popularity
        search_res = await client.search.search_notes("camping gear", sort="POPULARITY")
        export_to_csv(search_res.items, "search_result.csv")

if __name__ == "__main__":
    asyncio.run(run())
```
3. **Run**: `python search_and_export.py`
4. **Output location**: `search_result.csv`

### Example 3: Scrape Note Comments

1. **Create file**: `scrape_comments.py`
2. **Paste code**:
```python
import asyncio
from xhs_scraper import XHSClient

async def run():
    # Replace with your own cookies
    cookies = {"a1": "...", "web_session": "..."}
    async with XHSClient(cookies=cookies) as client:
        note_id = "65xxxxxxxxxxxxxxxx"
        comments = await client.comments.get_comments(note_id, max_pages=2)
        for comment in comments.items:
            print(f"{comment.user.nickname}: {comment.content}")

if __name__ == "__main__":
    asyncio.run(run())
```
3. **Run**: `python scrape_comments.py`
4. **Output**: Prints to terminal console

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
