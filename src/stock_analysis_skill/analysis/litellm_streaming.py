# -*- coding: utf-8 -*-
"""LiteLLM streaming helpers extracted from the analyzer core."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple


class LiteLLMStreamError(RuntimeError):
    """Error wrapper that records whether any text was already streamed."""

    def __init__(self, message: str, *, partial_received: bool = False):
        super().__init__(message)
        self.partial_received = partial_received


def normalize_usage(usage_obj: Any) -> Dict[str, Any]:
    """Normalize usage objects from LiteLLM responses or stream chunks."""
    if not usage_obj:
        return {}

    def _get_value(key: str) -> int:
        if isinstance(usage_obj, dict):
            return int(usage_obj.get(key) or 0)
        return int(getattr(usage_obj, key, 0) or 0)

    return {
        "prompt_tokens": _get_value("prompt_tokens"),
        "completion_tokens": _get_value("completion_tokens"),
        "total_tokens": _get_value("total_tokens"),
    }


def extract_stream_text(chunk: Any) -> str:
    """Extract provider-agnostic text delta from a LiteLLM stream chunk."""
    choices = chunk.get("choices") if isinstance(chunk, dict) else getattr(chunk, "choices", None)
    if not choices:
        return ""

    choice = choices[0]
    delta = choice.get("delta") if isinstance(choice, dict) else getattr(choice, "delta", None)
    message = choice.get("message") if isinstance(choice, dict) else getattr(choice, "message", None)

    content: Any = None
    if isinstance(delta, dict):
        content = delta.get("content")
    elif isinstance(delta, str):
        content = delta
    elif delta is not None:
        content = getattr(delta, "content", None)

    if content is None:
        if isinstance(message, dict):
            content = message.get("content")
        elif message is not None:
            content = getattr(message, "content", None)

    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)

    return content if isinstance(content, str) else ""


def consume_litellm_stream(
    stream_response: Any,
    *,
    model: str,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Consume a LiteLLM stream into a single response text payload."""
    chunks: List[str] = []
    usage: Dict[str, Any] = {}
    chars_received = 0
    next_emit_at = 1

    try:
        for chunk in stream_response:
            chunk_usage = chunk.get("usage") if isinstance(chunk, dict) else getattr(chunk, "usage", None)
            normalized_usage = normalize_usage(chunk_usage)
            if normalized_usage:
                usage = normalized_usage

            delta_text = extract_stream_text(chunk)
            if not delta_text:
                continue

            chunks.append(delta_text)
            chars_received += len(delta_text)
            if progress_callback and chars_received >= next_emit_at:
                progress_callback(chars_received)
                next_emit_at = chars_received + 160
    except Exception as exc:
        raise LiteLLMStreamError(
            f"{model} stream interrupted: {exc}",
            partial_received=chars_received > 0,
        ) from exc

    response_text = "".join(chunks).strip()
    if not response_text:
        raise LiteLLMStreamError(
            f"{model} stream returned empty response",
            partial_received=False,
        )

    if progress_callback and chars_received > 0:
        progress_callback(chars_received)

    return response_text, usage
