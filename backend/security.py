"""Security utilities, rate limiting, and request sanitization for LexiLaw."""

import asyncio
import logging
import time
import uuid
from typing import Callable, Dict, List, Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import settings

logger = logging.getLogger("lexilaw.security")


class InMemoryRateLimiter:
    """Thread-safe sliding window rate limiter in memory.
    
    Tracks timestamps of requests per client identifier and endpoint name.
    Automatically purges expired timestamps.
    """

    def __init__(self):
        self._records: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()

    def _get_key(self, client_id: str, endpoint: str) -> str:
        return f"{endpoint}:{client_id}"

    async def check_rate_limit(
        self,
        request: Request,
        endpoint_name: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        """Check if client has exceeded the allowed request limit within the window.
        
        Raises HTTPException(status_code=429) if exceeded.
        """
        if not settings.enable_rate_limiting:
            return

        client_ip = self.get_client_ip(request)
        key = self._get_key(client_ip, endpoint_name)
        now = time.time()
        window_start = now - window_seconds

        async with self._lock:
            timestamps = self._records.get(key, [])
            # Filter out timestamps outside the sliding window
            valid_timestamps = [t for t in timestamps if t > window_start]

            if len(valid_timestamps) >= limit:
                oldest = valid_timestamps[0]
                retry_after = max(1, int(oldest + window_seconds - now) + 1)
                self._records[key] = valid_timestamps
                logger.warning(
                    f"Rate limit exceeded for client {client_ip} on endpoint '{endpoint_name}' "
                    f"({len(valid_timestamps)}/{limit} in {window_seconds}s). Retry-After: {retry_after}s"
                )
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded for this operation. Please retry after {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)},
                )

            valid_timestamps.append(now)
            self._records[key] = valid_timestamps

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address safely, checking X-Forwarded-For if present."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # First IP in the comma-separated chain is the original client
            client_ip = forwarded.split(",")[0].strip()
            if client_ip:
                return client_ip

        if request.client and request.client.host:
            return request.client.host

        return "127.0.0.1"

    async def reset(self) -> None:
        """Reset all rate limit tracking records (useful in tests)."""
        async with self._lock:
            self._records.clear()


# Global limiter instance
limiter = InMemoryRateLimiter()


def rate_limit(endpoint_name: str, get_limit: Callable[[], int]):
    """FastAPI dependency for endpoint-level rate limiting."""
    async def dependency(request: Request):
        await limiter.check_rate_limit(
            request=request,
            endpoint_name=endpoint_name,
            limit=get_limit(),
            window_seconds=settings.rate_limit_window_seconds,
        )

    return dependency


# =========================================================================
# Authentication & Authorization (Optional for Academic Demo)
# =========================================================================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_optional_api_key(api_key: Optional[str] = Depends(api_key_header)) -> Optional[str]:
    """Verify API key when settings.api_key is configured.
    
    In academic development/demo mode (settings.api_key is None), passes through.
    In protected/production mode, rejects missing or invalid keys with 401.
    """
    if settings.api_key is not None:
        if not api_key or api_key != settings.api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key. Access is restricted.",
                headers={"WWW-Authenticate": "ApiKey"},
            )
    return api_key


# =========================================================================
# Security Headers & Request Size Middleware
# =========================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard defense-in-depth security response headers."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Enforce maximum body size limits early using Content-Length."""

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > settings.max_request_body_bytes:
                    req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": {
                                "code": "PAYLOAD_TOO_LARGE",
                                "message": (
                                    f"Request body exceeds maximum allowed size of "
                                    f"{settings.max_request_body_bytes} bytes."
                                ),
                                "request_id": req_id,
                            }
                        },
                        headers={"X-Request-ID": req_id},
                    )
            except ValueError:
                pass

        return await call_next(request)
