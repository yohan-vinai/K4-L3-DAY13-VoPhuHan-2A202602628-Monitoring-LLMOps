from __future__ import annotations

import os
from contextlib import contextmanager, nullcontext
from typing import Any

# Langfuse v4 treats empty strings loaded from .env as configured credentials.
# Use an explicit disabled sentinel so the SDK creates a no-op client and never
# initializes an exporter with empty Basic Auth credentials.
if not (os.getenv("LANGFUSE_PUBLIC_KEY", "").strip() and os.getenv("LANGFUSE_SECRET_KEY", "").strip()):
    os.environ["LANGFUSE_PUBLIC_KEY"] = "day13-local-disabled"
    os.environ["LANGFUSE_SECRET_KEY"] = "day13-local-disabled"
    os.environ["LANGFUSE_TRACING_ENABLED"] = "false"

try:
    from langfuse import get_client, observe, propagate_attributes

    LANGFUSE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - chỉ dùng khi chưa cài requirements
    LANGFUSE_SDK_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    class _DummyClient:
        def update_current_span(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

    def get_client():
        return _DummyClient()

    @contextmanager
    def propagate_attributes(**kwargs: Any):
        yield


def get_langfuse_client():
    return get_client()


def start_observation(client: Any, **kwargs: Any):
    """Start a child observation when supported by the configured SDK client."""
    if not tracing_enabled():
        return nullcontext(None)
    start = getattr(client, "start_as_current_observation", None)
    if callable(start):
        return start(**kwargs)
    return nullcontext(None)


def tracing_enabled() -> bool:
    explicitly_disabled = os.getenv("LANGFUSE_TRACING_ENABLED", "true").lower() in {
        "false",
        "0",
        "no",
    }
    return (
        LANGFUSE_SDK_AVAILABLE
        and not explicitly_disabled
        and bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
    )
