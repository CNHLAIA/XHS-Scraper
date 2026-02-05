"""Signature abstraction layer for xhshow library.

This module provides a clean interface to the xhshow signing functionality,
abstracting away the complexity of direct xhshow usage.
"""

from typing import Protocol, Dict, Any, Optional
from xhshow import Xhshow, SessionManager


class SignatureProvider(Protocol):
    """Protocol defining the signature generation interface.

    Any implementation must provide methods to generate signed headers
    for GET and POST requests to Xiaohongshu API endpoints.
    """

    def sign_get(
        self,
        uri: str,
        params: Optional[Dict[str, Any]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Generate signed headers for GET request.

        Args:
            uri: Target URI/endpoint path
            params: Query parameters dictionary
            cookies: Cookie dictionary for the session

        Returns:
            Dictionary containing signed headers:
                - x-s: Signature
                - x-s-common: Common signature
                - x-t: Timestamp
                - x-b3-traceid: B3 trace ID
                - x-xray-traceid: X-Ray trace ID
        """
        ...

    def sign_post(
        self,
        uri: str,
        payload: Optional[Dict[str, Any]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Generate signed headers for POST request.

        Args:
            uri: Target URI/endpoint path
            payload: Request body payload dictionary
            cookies: Cookie dictionary for the session

        Returns:
            Dictionary containing signed headers:
                - x-s: Signature
                - x-s-common: Common signature
                - x-t: Timestamp
                - x-b3-traceid: B3 trace ID
                - x-xray-traceid: X-Ray trace ID
        """
        ...


class XHShowSignatureProvider:
    """Implementation of SignatureProvider using xhshow library.

    This class wraps the xhshow signing functionality and provides
    a clean, documented interface for generating signed headers.
    """

    def __init__(self):
        """Initialize the signature provider with xhshow client."""
        self._client = Xhshow()
        self._session = SessionManager()

    def sign_get(
        self,
        uri: str,
        params: Optional[Dict[str, Any]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Generate signed headers for GET request.

        Args:
            uri: Target URI/endpoint path
            params: Query parameters dictionary
            cookies: Cookie dictionary for the session

        Returns:
            Dictionary containing signed headers required for the request.
        """
        if params is None:
            params = {}
        if cookies is None:
            cookies = {}

        headers = self._client.sign_headers_get(
            uri=uri,
            cookies=cookies,
            params=params,
            session=self._session,
        )
        return headers

    def sign_post(
        self,
        uri: str,
        payload: Optional[Dict[str, Any]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Generate signed headers for POST request.

        Args:
            uri: Target URI/endpoint path
            payload: Request body payload dictionary
            cookies: Cookie dictionary for the session

        Returns:
            Dictionary containing signed headers required for the request.
        """
        if payload is None:
            payload = {}
        if cookies is None:
            cookies = {}

        headers = self._client.sign_headers_post(
            uri=uri,
            cookies=cookies,
            payload=payload,
            session=self._session,
        )
        return headers
