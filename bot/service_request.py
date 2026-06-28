"""
Logged HTTP requests to Radarr, Sonarr, and Jellyfin.

Wraps requests.get/post with timing, response capture, and SQLite persistence
for the admin Logs UI. API keys are never stored in log rows.
"""

import json
import logging
import time
from typing import Any, Optional
from urllib.parse import urlparse

import requests

from bot.session_context import get_session_id

logger = logging.getLogger(__name__)


def _endpoint_path(url: str) -> str:
    """Return path + query string for logging (no host)."""
    parsed = urlparse(url)
    if parsed.query:
        return f"{parsed.path}?{parsed.query}"
    return parsed.path or url


def make_service_request(
    db,
    service: str,
    method: str,
    url: str,
    *,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    json_body: Optional[Any] = None,
    timeout: int = 10,
) -> requests.Response:
    """
    Perform an HTTP request to a media service and log it when db is set.

    Re-raises exceptions after logging, matching TMDB client behavior.
    """
    method_upper = method.upper()
    start_time = time.time()
    error_msg = None
    status_code = None
    response_body = None
    request_body_str = None

    if json_body is not None:
        request_body_str = json.dumps(json_body)

    try:
        if method_upper == 'GET':
            resp = requests.get(
                url, headers=headers, params=params, timeout=timeout,
            )
        elif method_upper == 'POST':
            resp = requests.post(
                url, headers=headers, params=params, json=json_body, timeout=timeout,
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        status_code = resp.status_code
        response_body = resp.text
        resp.raise_for_status()
        return resp
    except Exception as e:
        error_msg = str(e)
        raise
    finally:
        duration_ms = int((time.time() - start_time) * 1000)
        if db:
            db.log_service_api_request(
                service=service,
                method=method_upper,
                endpoint=_endpoint_path(url),
                params=params,
                request_body=request_body_str,
                duration_ms=duration_ms,
                status_code=status_code,
                response_body=response_body,
                error=error_msg,
                session_id=get_session_id(),
            )
