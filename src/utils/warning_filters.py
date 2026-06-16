"""Warning utilities for noisy third-party warnings."""

from __future__ import annotations

import warnings


def suppress_pydantic_serializer_warnings() -> None:
    """Ignore known noisy Pydantic serialization warnings from LLM libraries."""
    try:
        from pydantic_core._pydantic_core import PydanticSerializationUnexpectedValue

        warnings.filterwarnings(
            "ignore",
            category=PydanticSerializationUnexpectedValue,
            message=".*Pydantic serializer warnings:.*",
        )
    except Exception:
        # Keep this utility robust even if internals change.
        pass

    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        message=".*Pydantic serializer warnings:.*",
    )
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        message=".*PydanticSerializationUnexpectedValue.*",
    )
