"""
Cookie management utilities for XHS scraper.

Provides functions to:
- Load/save cookies from/to JSON files
- Extract cookies from Chrome browser database
- Validate cookie contents
"""

import json
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any


def load_cookies_from_file(path: str) -> Dict[str, Any]:
    """
    Load cookies from a JSON file.

    Args:
        path: Path to the JSON cookie file

    Returns:
        Dictionary of cookies

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cookie file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    return cookies


def save_cookies_to_file(cookies: Dict[str, Any], path: str) -> None:
    """
    Save cookies to a JSON file.

    Args:
        cookies: Dictionary of cookies to save
        path: Path where to save the JSON file

    Raises:
        ValueError: If cookies is empty
        IOError: If file cannot be written
    """
    if not cookies:
        raise ValueError("Cookies dictionary cannot be empty")

    # Ensure directory exists
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)


def extract_chrome_cookies() -> Dict[str, str]:
    """
    Extract cookies from Chrome browser database (Windows).

    Reads from Chrome's Cookies SQLite database and decrypts them
    (on Windows, cookies are stored in plaintext or require decryption).

    Returns:
        Dictionary mapping cookie names to values

    Raises:
        FileNotFoundError: If Chrome database not found
        sqlite3.OperationalError: If database is locked or corrupted
        Exception: If decryption fails
    """
    # Windows Chrome database path
    chrome_path = os.path.expandvars(
        r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies"
    )

    if not os.path.exists(chrome_path):
        raise FileNotFoundError(
            f"Chrome Cookies database not found at {chrome_path}. "
            "Make sure Chrome is installed and you have visited the target website."
        )

    # Create temporary copy to avoid "database is locked" error
    temp_db = os.path.join(os.path.dirname(chrome_path), "Cookies_temp")

    try:
        shutil.copy2(chrome_path, temp_db)
    except PermissionError:
        raise sqlite3.OperationalError(
            "Chrome database is locked. Please close Chrome and try again."
        )

    cookies_dict = {}

    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Query all cookies from Chrome database
        cursor.execute(
            'SELECT name, value FROM cookies WHERE host_key LIKE "%xiaohongshu%" OR host_key LIKE "%xhs%"'
        )

        rows = cursor.fetchall()
        for name, value in rows:
            cookies_dict[name] = value

        conn.close()
    except sqlite3.OperationalError as e:
        raise sqlite3.OperationalError(
            f"Failed to read Chrome database: {str(e)}. "
            "The database may be locked. Close Chrome and try again."
        )
    finally:
        # Clean up temporary database
        if os.path.exists(temp_db):
            try:
                os.remove(temp_db)
            except PermissionError:
                pass  # Ignore if we can't delete temp file

    return cookies_dict


def validate_cookies(cookies: Dict[str, Any]) -> bool:
    """
    Validate that cookies contain required keys for XHS authentication.

    Required keys:
    - a1: Authentication token
    - web_session: Web session identifier

    Args:
        cookies: Dictionary of cookies to validate

    Returns:
        True if valid, False otherwise

    Raises:
        ValueError: With details about missing required keys
    """
    if not isinstance(cookies, dict):
        raise ValueError("Cookies must be a dictionary")

    if not cookies:
        raise ValueError("Cookies dictionary cannot be empty")

    required_keys = {"a1", "web_session"}
    missing_keys = required_keys - set(cookies.keys())

    if missing_keys:
        raise ValueError(
            f"Missing required cookie keys: {missing_keys}. "
            f"Available keys: {set(cookies.keys())}"
        )

    # Validate values are not empty
    for key in required_keys:
        if not cookies[key] or not str(cookies[key]).strip():
            raise ValueError(f"Cookie '{key}' cannot be empty")

    return True
