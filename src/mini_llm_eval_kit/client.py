from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ClientError(RuntimeError):
    """Raised for endpoint, transport, or response parsing failures."""


@dataclass(frozen=True)
class ChatCompletionClient:
    endpoint: str
    model: str = "local-model"
    temperature: float = 0.0
    max_tokens: int = 256
    timeout: float = 60.0
    api_key: str | None = None

    def complete(self, prompt: str) -> str:
        if not self.endpoint:
            raise ClientError("endpoint is required unless --dry-run is used")

        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_body = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise ClientError(f"HTTP {exc.code}: {detail[:500]}") from exc
        except URLError as exc:
            raise ClientError(str(exc.reason)) from exc
        except TimeoutError as exc:
            raise ClientError(f"request timed out after {self.timeout} seconds") from exc

        try:
            payload: dict[str, Any] = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise ClientError("endpoint returned invalid JSON") from exc
        return extract_content(payload)


def extract_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ClientError("response missing non-empty choices list")
    first = choices[0]
    if not isinstance(first, dict):
        raise ClientError("first choice is not an object")
    message = first.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), str):
        return message["content"]
    if isinstance(first.get("text"), str):
        return first["text"]
    raise ClientError("response choice missing message.content or text")
