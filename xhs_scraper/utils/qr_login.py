"""QR code login helper for XHS scraper.

This module provides async QR code login functionality for Xiaohongshu authentication.
It handles QR code creation, status polling, and cookie retrieval.
"""

import asyncio
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

import aiohttp

from xhs_scraper.signature import SignatureProvider
from xhs_scraper.exceptions import APIError, XHSError


class QRLoginError(XHSError):
    """Raised when QR login fails or times out."""

    pass


class QRExpiredError(QRLoginError):
    """Raised when QR code expires without being scanned."""

    pass


async def create_qr_code(
    signature_provider: SignatureProvider,
    cookies: Optional[Dict[str, str]] = None,
) -> str:
    """Create a new QR code for login.

    Args:
        signature_provider: SignatureProvider instance for request signing
        cookies: Optional existing cookies for the session

    Returns:
        QR code ID string

    Raises:
        APIError: If QR creation fails
    """
    if cookies is None:
        cookies = {}

    uri = "/api/sns/web/v1/login/qrcode/create"
    payload = {}

    headers = signature_provider.sign_post(uri, payload, cookies)
    headers.update(
        {
            "Content-Type": "application/json;charset=UTF-8",
        }
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://edith.xiaohongshu.com{uri}",
            json=payload,
            headers=headers,
            cookies=cookies,
        ) as resp:
            if resp.status != 200:
                data = await resp.json()
                raise APIError(resp.status, f"Failed to create QR code: {data}", data)

            data = await resp.json()

            if not data.get("success"):
                raise APIError(
                    resp.status, f"QR code creation failed: {data.get('msg')}", data
                )

            qr_data = data.get("data", {})
            qr_id = qr_data.get("qrCode", {}).get("qrcodeId")

            if not qr_id:
                raise APIError(resp.status, "No QR code ID in response", data)

            return qr_id


async def poll_qr_status(
    qr_id: str,
    signature_provider: SignatureProvider,
    cookies: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Poll QR code status to check if it's been scanned.

    Args:
        qr_id: QR code ID returned from create_qr_code()
        signature_provider: SignatureProvider instance for request signing
        cookies: Optional existing cookies for the session

    Returns:
        Dictionary containing:
            - "scanned": bool indicating if QR was scanned
            - "cookies": dict of auth cookies if scan is complete

    Raises:
        APIError: If status check fails
        QRExpiredError: If QR code has expired
    """
    if cookies is None:
        cookies = {}

    uri = "/api/sns/web/v1/login/qrcode/status"
    params = {"qrcodeId": qr_id}

    headers = signature_provider.sign_get(uri, params, cookies)

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://edith.xiaohongshu.com{uri}",
            params=params,
            headers=headers,
            cookies=cookies,
        ) as resp:
            if resp.status != 200:
                data = await resp.json()
                raise APIError(resp.status, f"Failed to check QR status: {data}", data)

            data = await resp.json()

            if not data.get("success"):
                msg = data.get("msg", "Unknown error")
                if "expired" in msg.lower():
                    raise QRExpiredError(f"QR code expired: {msg}")
                raise APIError(resp.status, f"QR status check failed: {msg}", data)

            status_data = data.get("data", {})
            status = status_data.get("status")

            # Status codes: 0 = pending, 1 = scanned but not confirmed, 2 = confirmed/logged in
            if status == 2:
                # Login successful, extract cookies
                cookies_list = status_data.get("cookies", [])
                result_cookies = {}
                for cookie in cookies_list:
                    if isinstance(cookie, dict):
                        name = cookie.get("name")
                        value = cookie.get("value")
                        if name and value:
                            result_cookies[name] = value

                return {
                    "scanned": True,
                    "cookies": result_cookies,
                }

            return {
                "scanned": False,
                "cookies": {},
            }


async def qr_login(
    signature_provider: SignatureProvider,
    cookies: Optional[Dict[str, str]] = None,
    timeout_seconds: int = 300,
    poll_interval_seconds: float = 1.0,
) -> Dict[str, str]:
    """Perform QR code login with polling.

    Creates a QR code and polls until it's scanned or timeout is reached.

    Args:
        signature_provider: SignatureProvider instance for request signing
        cookies: Optional existing cookies for the session
        timeout_seconds: Maximum time to wait for QR scan (default 300 = 5 minutes)
        poll_interval_seconds: Time between status checks in seconds (default 1.0)

    Returns:
        Dictionary of authentication cookies on success

    Raises:
        QRLoginError: If login fails for any reason
        QRExpiredError: If QR code expires before being scanned
        APIError: If API requests fail
    """
    if cookies is None:
        cookies = {}

    # Create QR code
    try:
        qr_id = await create_qr_code(signature_provider, cookies)
    except APIError as e:
        raise QRLoginError(f"Failed to create QR code: {e}")

    # Poll until scanned or timeout
    start_time = time.time()
    deadline = start_time + timeout_seconds

    while time.time() < deadline:
        try:
            status = await poll_qr_status(qr_id, signature_provider, cookies)

            if status.get("scanned") and status.get("cookies"):
                return status["cookies"]

            # Wait before next poll
            await asyncio.sleep(poll_interval_seconds)

        except QRExpiredError:
            raise
        except APIError as e:
            # Continue polling on non-fatal errors
            await asyncio.sleep(poll_interval_seconds)

    # Timeout reached
    raise QRLoginError(
        f"QR code login timeout after {timeout_seconds} seconds - QR was not scanned"
    )
