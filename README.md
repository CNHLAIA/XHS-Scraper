# xhs-scraper - Async Python scraper for Xiaohongshu (小红书/RED)

An asynchronous Python library for scraping Xiaohongshu (XHS) data including notes, users, comments, and search results.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import asyncio
from xhs_scraper import XHSClient

async def main():
    cookies = "your_cookies_here"
    async with XHSClient(cookies=cookies) as client:
        # Get a specific note
        note = await client.notes.get_note("note_id_here")
        print(note.title)

if __name__ == "__main__":
    asyncio.run(main())
```

## Cookie Setup

### Browser DevTools Method
1. Open Xiaohongshu in your browser and log in.
2. Press `F12` to open DevTools.
3. Go to the **Network** tab.
4. Refresh the page or perform an action.
5. Click on any request to `edith.xiaohongshu.com`.
6. Look for `Cookie` in the **Request Headers** and copy the entire string.

### Chrome Extraction
If you are using Google Chrome on your local machine, you can extract cookies automatically:

```python
from xhs_scraper.utils import extract_chrome_cookies

cookies = extract_chrome_cookies()
```

### QR Login
You can also log in via QR code:

```python
from xhs_scraper import qr_login

async def login():
    cookies = await qr_login()
    print(f"Logged in! Cookies: {cookies}")
```

## API Reference

### Client Initialization
- `XHSClient(cookies, rate_limit=1.0)`: Main client for interacting with the XHS API.

### Notes
- `client.notes.get_note(note_id)`: Get detailed information for a single note.
- `client.notes.get_user_notes(user_id)`: List all notes posted by a specific user.

### Users
- `client.users.get_user_info(user_id)`: Get profile information for a user.
- `client.users.get_self_info()`: Get your own profile information.

### Comments
- `client.comments.get_comments(note_id)`: Fetch top-level comments for a note.
- `client.comments.get_sub_comments(comment_id)`: Fetch replies to a specific comment.

### Search
- `client.search.search_notes(keyword, sort="general")`: Search for notes using keywords.

## Export Data
The library provides built-in utilities for exporting data:

```python
from xhs_scraper.utils import export_to_json, export_to_csv

# Export to JSON
export_to_json(data, "notes.json")

# Export to CSV
export_to_csv(data, "notes.csv")
```

## Error Handling

The library defines several custom exceptions for common API issues:

- `XHSError`: Base exception class.
- `SignatureError (461)`: Raised when the request signature validation fails.
- `CaptchaRequiredError (471)`: Raised when the API triggers a captcha.
