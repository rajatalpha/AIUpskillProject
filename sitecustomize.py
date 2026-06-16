"""Project-wide warning policy.

Suppresses known noisy Pydantic serialization warnings emitted by LiteLLM/OpenAI
response object conversion in this environment. This keeps runtime output clean while
we keep compatibility via the pinned dependency versions in ``requirements.txt``.
"""

import warnings

try:
    from pydantic_core._pydantic_core import PydanticSerializationUnexpectedValue

    warnings.filterwarnings(
        "ignore",
        category=PydanticSerializationUnexpectedValue,
        message="Pydantic serializer warnings:.*",
    )
except Exception:
    # Keep startup resilient if internal pydantic layout changes.
    pass

# Fallback for environments where the warning is emitted as generic UserWarning.
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Pydantic serializer warnings:",
)

# Handle variants where module/message formatting differs slightly.
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=".*PydanticSerializationUnexpectedValue.*",
)
