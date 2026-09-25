from collections.abc import Mapping
from typing import Any


class LearningGenerationValidationError(ValueError):
    """Raised when n8n does not return a valid learning package."""


def normalize_learning_generation_response(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise LearningGenerationValidationError("n8n response must be a JSON object")

    package = payload.get("output") if "output" in payload else payload
    if not isinstance(package, Mapping):
        raise LearningGenerationValidationError("learning package must be a JSON object")

    return dict(package)
