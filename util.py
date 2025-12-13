import logging
from typing import Literal

import httpcore
import httpx
from fastapi import HTTPException
from httpx import Response
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type(
        (
            httpx.ConnectError,
            httpcore.ConnectError,
            httpx.HTTPStatusError,
        )
    ),
    reraise=True,
)
async def _send_request_with_retry(
        method: Literal['GET', 'POST', 'PUT'],
        url: str,
        headers: dict = None,
        data: dict = None,
) -> Response:
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response


async def send_request(
        method: Literal['GET', 'POST', 'PUT'],
        url: str,
        headers: dict = None,
        data: dict = None,
) -> dict | str:
    try:
        response = await _send_request_with_retry(method, url, headers, data)
    except (httpx.ConnectError, httpcore.ConnectError) as e:
        detail = f"Connection failed after retries: {e}"
        logging.exception(detail)
        raise HTTPException(status_code=503, detail=detail)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        detail = f"Unknown error: {e}"
        logging.exception(detail)
        raise HTTPException(status_code=500, detail=detail)

    content_type = response.headers["content-type"]
    if "application/json" in content_type:
        return response.json()
    return response.text
