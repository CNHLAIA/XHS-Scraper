# XHS Scraper Public API
from xhs_scraper.client import XHSClient
from xhs_scraper.exceptions import (
    XHSError,
    SignatureError,
    CaptchaRequiredError,
    CookieExpiredError,
    RateLimitError,
    APIError,
)
from xhs_scraper.utils.cookies import (
    load_cookies_from_file,
    save_cookies_to_file,
    extract_chrome_cookies,
)
from xhs_scraper.utils.qr_login import qr_login
from xhs_scraper.utils.export import export_to_json, export_to_csv
from xhs_scraper.utils.media import download_media

__all__ = [
    # Client
    "XHSClient",
    # Exceptions
    "XHSError",
    "SignatureError",
    "CaptchaRequiredError",
    "CookieExpiredError",
    "RateLimitError",
    "APIError",
    # Cookie utilities
    "load_cookies_from_file",
    "save_cookies_to_file",
    "extract_chrome_cookies",
    # QR login
    "qr_login",
    # Export utilities
    "export_to_json",
    "export_to_csv",
    # Media utilities
    "download_media",
]
